import os
from typing import Optional

from langchain_community.embeddings import DashScopeEmbeddings

from app.conf.app_config import EmbeddingConfig


class EmbeddingClientManager:
    def __init__(self, embedding_config: EmbeddingConfig):
        self.embedding_config = embedding_config
        self.client: Optional[DashScopeEmbeddings] = None

    def init(self):
        self.client = DashScopeEmbeddings(
            model=self.embedding_config.model,
            dashscope_api_key=os.getenv("DASH_SCOPE_API_KEY")
        )


if __name__ == '__main__':
    # 1. 初始化阿里千问 Embedding 模型
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=os.getenv("DASH_SCOPE_API_KEY")
    )

    vector = embeddings.embed_query("hello world!")

    print(vector)
