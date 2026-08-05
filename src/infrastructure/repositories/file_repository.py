from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import FileRecord
from src.domain.repositories import IFileRepository
from src.infrastructure.models.file_record import FileRecordOrm


class FileRepository(IFileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(orm: FileRecordOrm) -> FileRecord:
        return FileRecord(
            id=orm.id,
            name=orm.name,
            content=orm.content,
            downloaded_at=orm.downloaded_at,
            is_downloaded=orm.is_downloaded,
        )

    async def add_or_update(self, record: FileRecord) -> FileRecord:
        orm = await self._session.get(FileRecordOrm, record.id)
        if orm is None:
            orm = FileRecordOrm(
                name=record.name,
                content=record.content,
                downloaded_at=record.downloaded_at,
                is_downloaded=record.is_downloaded,
            )
            self._session.add(orm)
        else:
            orm.content = record.content
            orm.downloaded_at = record.downloaded_at
            orm.is_downloaded = record.is_downloaded
        await self._session.flush()
        return self._to_domain(orm)

    async def get_all(self, offset: int, limit: int) -> list[FileRecord]:
        statement = (
            select(FileRecordOrm)
            .order_by(FileRecordOrm.downloaded_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_downloaded(self) -> list[FileRecord]:
        statement = select(FileRecordOrm).where(FileRecordOrm.is_downloaded.is_(True))
        result = await self._session.execute(statement)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_names(self, names: list[str]) -> list[FileRecord]:
        statement = select(FileRecordOrm).where(FileRecordOrm.name.in_(names))
        result = await self._session.execute(statement)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count_downloaded(self) -> int:
        statement = (
            select(func.count())
            .select_from(FileRecordOrm)
            .where(FileRecordOrm.is_downloaded.is_(True))
        )
        result = await self._session.execute(statement)
        return result.scalar_one()

    async def get_by_ids(self, ids: list[int]) -> list[FileRecord]:
        statement = select(FileRecordOrm).where(FileRecordOrm.id.in_(ids))
        result = await self._session.execute(statement)
        return [self._to_domain(row) for row in result.scalars().all()]
