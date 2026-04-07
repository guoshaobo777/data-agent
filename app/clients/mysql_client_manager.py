import asyncio
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:
    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def _get_async_engine_url(self):
        # 使用 asyncmy 作为驱动
        return (
            f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}"
            f"@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}"
            "?charset=utf8mb4"
        )

    def _get_sync_engine_url(self):
        # 使用 pymysql 作为驱动
        return (
            f"mysql+pymysql://{self.db_config.user}:{self.db_config.password}"
            f"@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}"
            "?charset=utf8mb4"
        )

    def init(self):
        self.engine = create_async_engine(
            url=self._get_async_engine_url(),
            pool_size=20,
            pool_pre_ping=True
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=True,
            expire_on_commit=False,
            autobegin=True
        )

    async def close(self):
        await self.engine.dispose()

dw_mysql_client_manager: MysqlClientManager = MysqlClientManager(app_config.db_dw)
meta_mysql_client_manager: MysqlClientManager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    meta_mysql_client_manager.init()

    async def test():
        async with meta_mysql_client_manager.session_factory() as session:
            session: AsyncSession
            result = await session.execute(text("show tables;"))
            rows = result.fetchall()
            print(rows)

    asyncio.run(test())