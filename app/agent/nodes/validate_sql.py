from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "验证SQL", "status": "running"})
    sql = state["sql"]

    dw_mysql_repository = runtime.context['dw_mysql_repository']

    try:
        await dw_mysql_repository.validate_sql(sql)
        writer({"type": "progress", "step": "验证SQL", "status": "success"})
        logger.info(f"验证SQL成功: {sql}")
        return {"error": None}
    except Exception as e:
        writer({"type": "progress", "step": "验证SQL", "status": "error"})
        logger.error(f"验证SQL失败: {str(e)}")
        # 验证SQL失败不能抛出异常终止流程，而是应该保存错误信息供下一步矫正
        return {"error": str(e)}
