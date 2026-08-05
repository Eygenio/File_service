from collections.abc import AsyncGenerator

from fastapi import Depends

from src.application.services.download_service import DownloadService
from src.application.services.stats_service import StatsService
from src.db.database import async_session_factory
from src.infrastructure.unit_of_work import UnitOfWork


async def get_uow() -> AsyncGenerator[UnitOfWork]:
    async with async_session_factory() as session:
        yield UnitOfWork(session)


async def get_download_service(uow: UnitOfWork = Depends(get_uow)) -> DownloadService:
    return DownloadService(uow, candidate_id="default")


async def get_stats_service(uow: UnitOfWork = Depends(get_uow)) -> StatsService:
    return StatsService(uow)
