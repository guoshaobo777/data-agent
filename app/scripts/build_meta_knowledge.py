import asyncio
from argparse import ArgumentParser
from pathlib import Path

import main
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.clients.es_client_manager import es_client_manager
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.services.meta_knowleddge_service import MetaKnowledgeService


async def build(config_path: Path):
    # 初始化数据层客户端
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()

    # 构建元知识库
    async with(
        meta_mysql_client_manager.session_factory() as meta_session,
        dw_mysql_client_manager.session_factory() as dw_session,
    ):
        # 创建元数据 repository 实例
        meta_mysql_repository = MetaMySQLRepository(meta_session)
        dw_mysql_repository = DWMySQLRepository(dw_session)
        column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
        embedding_client = embedding_client_manager.client
        value_es_repository = ValueESRepository(es_client_manager.client)
        metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)

        # 创建 MetaKnowledgeService 实例
        meta_knowledge_service = MetaKnowledgeService(
            meta_mysql_repository=meta_mysql_repository,
            dw_mysql_repository=dw_mysql_repository,
            column_qdrant_repository=column_qdrant_repository,
            embedding_client=embedding_client,
            value_es_repository=value_es_repository,
            metric_qdrant_repository=metric_qdrant_repository
        )
        # 构建元知识库
        await meta_knowledge_service.build(config_path=config_path)


    # 关闭数据层客户端
    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--conf')
    args = parser.parse_args()
    if args.conf:
        config_path = Path(args.conf)
    else:
        config_path = main.get_project_path() / 'conf' / 'meta_config.yaml'
    # 检查 config_path
    assert config_path.exists(), f"配置文件 {config_path} 不存在"
    asyncio.run(build(config_path))
