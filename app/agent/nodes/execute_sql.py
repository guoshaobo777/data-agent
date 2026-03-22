from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def execute_sql(state: DataAgentState, context: Runtime[DataAgentContext]):
    pass