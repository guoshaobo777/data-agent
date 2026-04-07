from dataclasses import asdict

from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError
from loguru import logger

from app.entities.value_info import ValueInfo


class ValueESRepository:
    index_name = "data-agent-value"
    index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {
                "type": "keyword"
            },
            "value": {
                "type": "text",
                "analyzer": "standard",
                "search_analyzer": "standard"
            },
            "column_id": {
                "type": "keyword"
            }
        }
    }

    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    async def ensure_index_exists(self):
        if not await self.es_client.indices.exists(index=self.index_name):
            await self.es_client.indices.create(index=self.index_name, mappings=self.index_mappings)

    async def index(self, value_infos: list[ValueInfo], batch_size=20):
        for i in range(0, len(value_infos), batch_size):
            batch = value_infos[i: i + batch_size]
            operations = []
            for value_info in batch:
                operations.append({
                    "index": {
                        "_index": self.index_name,
                        "_id": value_info.id
                    }
                })
                operations.append(asdict(value_info))
            await self.es_client.bulk(operations=operations)

    async def search(self, keyword: str, score_threshold: float = 0.6, limit: int = 5) -> list[ValueInfo]:
        try:
            result = await self.es_client.search(
                index=self.index_name,
                query={
                    "match": {
                        "value": keyword
                    }
                },
                min_score=score_threshold,
                size=limit
            )
            logger.info(f"搜索值信息: {keyword}, 搜索结果: {result}")  # 打印搜索信息
            return [ValueInfo(**hit["_source"]) for hit in result["hits"]["hits"]]
        except NotFoundError:
            # 元数据索引尚未构建时，降级为空结果，避免整条链路失败
            logger.warning(f"索引不存在: {self.index_name}，跳过字段取值召回")
            return []