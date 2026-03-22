from dataclasses import asdict

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance,VectorParams

from app.conf.app_config import app_config
from app.entities.column_info import ColumnInfo


class ColumnQdrantRepository:
    collection_name: str = "data-agent-column"

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
                    distance=Distance.COSINE
                )
            )

    async def upsert(self,
                     ids: list[str],
                     embeddings: list[list[float]],
                     payloads: list[ColumnInfo],
                     batch_size: int = 20):
        zipped = list(zip(ids, embeddings, payloads))
        for i in range(0, len(zipped), batch_size):
            batch = zipped[i: i + batch_size]
            batch_points = [
                PointStruct(
                    id=id,
                    vector=embeddings,
                    payload=asdict(payloads)
                )
                for id, embeddings, payloads in batch
            ]
            await self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch_points
            )

