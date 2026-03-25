from dataclasses import asdict

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, QueryResponse

from app.conf.app_config import app_config
from app.entities.metric_info import MetricInfo


class MetricQdrantRepository:
    collection_name = "data-agent-metric"

    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client

    async def ensure_collection_exists(self):
        if not await self.qdrant_client.collection_exists(
            self.collection_name
        ):
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=app_config.qdrant.embedding_size,
                    distance=Distance.COSINE,
                )
            )

    async def upsert(self,
                     ids: list[str],
                     embeddings: list[list[float]],
                     payloads: list[MetricInfo],
                     batch_size: int = 20):
        zipped = list(zip(ids, embeddings, payloads))
        for i in range(0, len(zipped), batch_size):
            batch = zipped[i: i + batch_size]
            batch_points = [
                PointStruct(
                    id=id,
                    vector=embedding,
                    payload=asdict(payload)
                )
                for id, embedding, payload in batch
            ]
            await self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch_points
            )

    async def search(self, embedding: list[float], score_threshold: float = 0.6, limit: int = 5) -> list[MetricInfo]:
        result: QueryResponse = await self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True
        )
        return [MetricInfo(**point.payload) for point in result.points]