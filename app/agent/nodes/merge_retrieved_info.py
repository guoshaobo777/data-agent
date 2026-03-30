from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState, MetricInfoState, ColumnInfoState
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "合并召回信息", "status": "running"})
    # 已召回信息
    retrieved_columns = state['retrieved_columns']
    retrieved_values = state['retrieved_values']
    retrieved_metrics = state['retrieved_metrics']

    # 获取所需依赖
    meta_mysql_repository = runtime.context['meta_mysql_repository']
    retrieved_columns_map: dict[str, ColumnInfo] = {
        retrieved_column.id: retrieved_column for retrieved_column in retrieved_columns
    }

    # 合并表格信息
    table_infos: list[TableInfoState] = []

    try:
        # 将指标信息相关的列添加到字段信息列表
        for retrieved_metric in retrieved_metrics:
            relevant_columns = retrieved_metric.relevant_columns
            for relevant_column in relevant_columns:
                if relevant_column not in retrieved_columns_map:
                    column_info = await meta_mysql_repository.get_column_info_by_id(relevant_column)
                    retrieved_columns_map[relevant_column] = column_info

        # 将字段取值合并到字段信息列表
        for retrieved_value in retrieved_values:
            column_id = retrieved_value.column_id
            column_value = retrieved_value.value

            if column_id not in retrieved_columns_map:
                column_info = await meta_mysql_repository.get_column_info_by_id(column_id=column_id)
                retrieved_columns_map[column_id] = column_info
            if column_value not in retrieved_columns_map[column_id].examples:
                retrieved_columns_map[column_id].examples.append(column_value)

        # 按照字段所属的表ID进行分组，得到 table_id -> columns 的映射
        table_to_columns_map: dict[str, list[ColumnInfo]] = {}
        for column in retrieved_columns_map.values():
            table_id = column.table_id
            if table_id not in table_to_columns_map:
                table_to_columns_map[table_id] = []
            table_to_columns_map[table_id].append(column)

        # 显式添加每个表的主外键
        for table_id in table_to_columns_map.keys():
            # 查询主外键字段
            key_columns = await meta_mysql_repository.get_key_columns_by_table_id(table_id)
            # 确定当前表已有的所有列的ID
            column_ids = [column.id for column in table_to_columns_map[table_id]]

            for key_column in key_columns:
                if key_column.id not in column_ids:
                    table_to_columns_map[table_id].append(key_column)

        # 将 table_id -> columns 映射 转换为 list[TableInfoState]
        for table_id, column_infos in table_to_columns_map.items():
            table: TableInfo = await meta_mysql_repository.get_table_info_by_id(table_id)
            columns = [
                ColumnInfoState(
                    name=column_info.name,
                    type=column_info.type,
                    role=column_info.role,
                    examples=column_info.examples,
                    description=column_info.description,
                    alias=column_info.alias
                )
                for column_info in column_infos
            ]
            table_info_state = TableInfoState(
                name=table.name,
                role=table.role,
                description=table.description,
                columns=columns
            )
            table_infos.append(table_info_state)

        # 处理指标信息
        metric_infos: list[MetricInfoState] = [
            MetricInfoState(
                name=metric_info.name,
                description=metric_info.description,
                relevant_columns=metric_info.relevant_columns,
                alias=metric_info.alias
            )
            for metric_info in retrieved_metrics
        ]
        writer({"type": "progress", "step": "合并召回信息", "status": "success"})
        logger.info(
            f"合并召回信息: 表信息-{[table_info['name'] for table_info in table_infos]}, 指标信息-{[metric_info['name'] for metric_info in metric_infos]}")
        return {"table_infos": table_infos, "metric_infos": metric_infos}
    except Exception as e:
        writer({"type": "progress", "step": "合并召回信息", "status": "error"})
        logger.error(f"合并召回信息失败: {str(e)}")
        raise e
