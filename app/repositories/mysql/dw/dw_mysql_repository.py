from sqlalchemy.ext.asyncio import AsyncSession


class DWMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session