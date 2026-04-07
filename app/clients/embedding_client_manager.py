import os
from typing import Optional

from langchain_community.embeddings import DashScopeEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, embedding_config: EmbeddingConfig):
        self.embedding_config = embedding_config
        self.client: Optional[DashScopeEmbeddings] = None

    def init(self):
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("DASH_SCOPE_API_KEY")
        self.client = DashScopeEmbeddings(
            model=self.embedding_config.model,
            dashscope_api_key=dashscope_api_key
        )
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("DASH_SCOPE_API_KEY")
    # 1. 初始化阿里千问 Embedding 模型
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=dashscope_api_key
    )

    vector = embeddings.embed_query("hello world!")

    print(vector)
