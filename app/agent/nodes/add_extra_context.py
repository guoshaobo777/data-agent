from datetime import datetime

from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "添加额外信息", "status": "running"})
    dw_mysql_repository = runtime.context['dw_mysql_repository']

    try:
        # 当前的时间信息
        today = datetime.today()
        # 日期
        date = today.strftime("%Y-%m-%d")
        # 星期
        weekday = today.strftime("%A")
        # 季度
        quarter = f"Q{(today.month - 1) // 3 + 1}"

        date_info = DateInfoState(date=date, weekday=weekday, quarter=quarter)
        # 数据仓库环境信息
        db_info = await dw_mysql_repository.get_db_info()
        writer({"type": "progress", "step": "添加额外信息", "status": "success"})
        logger.info(f"额外上下文信息: 数据库信息-{db_info}. 日期信息-{date_info}")
        return {"date_info": date_info, "db_info": db_info}
    except Exception as e:
        writer({"type": "progress", "step": "添加额外信息", "status": "error"})
        logger.error(f"添加额外信息失败: {str(e)}")
        raise e
