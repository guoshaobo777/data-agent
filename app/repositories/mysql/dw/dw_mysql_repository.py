import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import dw_mysql_client_manager


class DWMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        pre_sql = f"show columns from `{table_name}` "
        result = await self.session.execute(text(pre_sql))

        return {row[0]: row[1] for row in result.fetchall()}

    async def get_column_values(self, table_name:str, column_name:str, limit: int):
        sql = f"select distinct {column_name} from `{table_name}` limit {limit}"
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()

    async def execute_sql(self, sql: str):
        result = await self.session.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]

    async def get_db_info(self):
        result = await self.session.execute(text("select version()"))
        version = result.scalar()

        dialect = self.session.get_bind().dialect.name
        return {"dialect": dialect, "version": version}
    async def validate_sql(self, sql):
        await self.session.execute(text(f"explain {sql}"))


if __name__ == "__main__":
    dw_mysql_client_manager.init()
    async def test():
        async with dw_mysql_client_manager.session_factory() as session:
            session: AsyncSession
            dw_my_sql_repository = DWMySQLRepository(session)
            print(await dw_my_sql_repository.get_column_types("dim_date"))
            print(await dw_my_sql_repository.get_column_values("dim_date", "date_id", 10))
    asyncio.run(test())