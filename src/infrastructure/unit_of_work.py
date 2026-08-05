from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.file_repository import FileRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.files = FileRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
