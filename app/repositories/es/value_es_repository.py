from elasticsearch import AsyncElasticsearch


class ValueESRepository:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client