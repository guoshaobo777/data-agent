from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "执行SQL", "status": "running"})

    sql = state["sql"]

    dw_mysql_repository = runtime.context["dw_mysql_repository"]

    try:
        # TODO 拦截恶意SQL
        result = await dw_mysql_repository.execute_sql(sql)
        writer({"type": "progress", "step": "执行SQL", "status": "success"})
        writer({"type": "result", "data": result})
        logger.info(f"执行 SQL 结果: {result}")
    except Exception as e:
        writer({"type": "progress", "step": "执行SQL", "status": "error"})
        logger.error(f"执行 SQL 失败: {str(e)}")
        raise e
    return