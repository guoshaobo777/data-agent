from pathlib import Path

from langchain_core.embeddings import Embeddings
from loguru import logger
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.repositories.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.dw_mysql_repository import DWMySQLRepository
from app.repositories.meta_mysql_repository import MetaMySQLRepository
from app.repositories.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.value_es_repository import ValueESRepository


class MetaKnowledgeService:
    def __init__(
        self,
        meta_mysql_repository: MetaMySQLRepository,
        dw_mysql_repository: DWMySQLRepository,
        column_qdrant_repository: ColumnQdrantRepository,
        embedding_client: Embeddings,
        value_es_repository: ValueESRepository,
        metric_qdrant_repository: MetricQdrantRepository,
    ):
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.embedding_client = embedding_client
        self.value_es_repository = value_es_repository
        self.metric_qdrant_repository = metric_qdrant_repository

    async def build(self, config_path: Path):
        # 1. 加载配置文件
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        logger.info(f"加载配置文件: {meta_config}")

        # 2. 处理表信息
        if meta_config.tables:
            # 2.1 保存表信息 到 meta 数据库
            column_infos = await self._save_tables_to_meta_db(meta_config)
            logger.info(f"保存表信息 到 meta 数据库")
            # 2.2 为字段信息建立向量索引
            await self._save_columns_info_to_qdrant(column_infos)
            logger.info(f"为字段信息建立向量索引")
            # 2.3 为字段取值建立全文索引
            await self._save_value_info_to_es(meta_config, column_infos)
            logger.info(f"为字段取值建立全文索引")


        # 3. 处理指标信息
        if meta_config.metrics:
            # 3.1 保存指标信息到 meta 数据库
            metric_infos = await self._save_metrics_to_meta_db(meta_config)
            logger.info(f"保存指标信息到 meta 数据库")
            # 3.2 为指标信息建立 向量索引
            await self._save_metrics_info_to_qdrant(metric_infos)
            logger.info(f"为指标信息建立 向量索引")

        logger.info(f"元数据知识库构建完成")

    async def _save_tables_to_meta_db(self, meta_config: MetaConfig) -> list[ColumnInfo]:
        pass
