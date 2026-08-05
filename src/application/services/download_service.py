import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime

from src.application.constants import MAX_DOWNLOADS_PER_REQUEST
from src.domain.entities import FileRecord
from src.infrastructure.clients.file_api_client import FileApiClient
from src.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int], Awaitable[None]]


class DownloadService:
    def __init__(self, uow: UnitOfWork, candidate_id: str) -> None:
        self.uow = uow
        self.candidate_id = candidate_id

    async def run(
        self,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        async with FileApiClient(self.candidate_id) as client:
            while True:
                names = await client.get_file_names()
                if not names:
                    logger.info("All files downloaded")
                    break

                total = len(names)
                if progress_callback:
                    await progress_callback(total, 0)

                for i in range(0, total, MAX_DOWNLOADS_PER_REQUEST):
                    batch = names[i : i + MAX_DOWNLOADS_PER_REQUEST]
                    contents = await client.download_files(batch)
                    for name, content in contents.items():
                        record = FileRecord(
                            name=name,
                            content=content,
                            downloaded_at=datetime.utcnow(),
                            is_downloaded=True,
                        )
                        await self.uow.files.add_or_update(record)

                    await client.mark_downloaded(batch)
                    await self.uow.commit()
                    downloaded = min(i + len(batch), total)
                    if progress_callback:
                        await progress_callback(total, downloaded)
                    logger.info(
                        "Downloaded batch of %d files (%d/%d)",
                        len(batch),
                        downloaded,
                        total,
                    )
                    await asyncio.sleep(2)
