from qdrant_client import QdrantClient


class MetricQdrantRepository:
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client