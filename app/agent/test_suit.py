from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


@asynccontextmanager
async def create_runtime_context() -> AsyncGenerator[DataAgentContext, None]:
    """
    创建测试使用的 Runtime 上下文管理器
    使用 yield 提供 context，并自动清理资源
    :return:
    """
    # 初始化客户端
    embedding_client_manager.init()
    es_client_manager.init()
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()
    qdrant_client_manager.init()

    # 创建langgraph运行时上下文
    try:
        async with meta_mysql_client_manager.session_factory() as meta_session, \
                dw_mysql_client_manager.session_factory() as dw_session:
            # 创建数据层Repository
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DWMySQLRepository(dw_session)
            column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
            metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)
            value_es_repository = ValueESRepository(es_client_manager.client)

            context = DataAgentContext(
                embedding_client=embedding_client_manager.client,
                column_qdrant_repository=column_qdrant_repository,
                metric_qdrant_repository=metric_qdrant_repository,
                value_es_repository=value_es_repository,
                meta_mysql_repository=meta_mysql_repository,
                dw_mysql_repository=dw_mysql_repository
            )

            yield context
    finally:
        # 关闭客户端
        await qdrant_client_manager.close()
        await es_client_manager.close()
        await meta_mysql_client_manager.close()
        await dw_mysql_client_manager.close()


async def test_node_framework(state: DataAgentState, func: Callable):
    graph_builder = StateGraph(
        state_schema=DataAgentState,
        context_schema=DataAgentContext,
    )

    graph_builder.add_node(func.__name__, func)
    graph_builder.add_edge(START, func.__name__)
    graph_builder.add_edge(func.__name__, END)
    graph = graph_builder.compile()

    async with create_runtime_context() as context:
        async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
            print(chunk)
