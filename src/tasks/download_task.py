import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from celery import Task

from src.application.constants import TASK_STATE_PROGRESS
from src.application.services.download_service import DownloadService
from src.celery_app import celery
from src.db.database import async_session_factory
from src.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

NSK_TZ = timezone(timedelta(hours=7))


@celery.task(bind=True)
def download_task(self: Task) -> dict:
    start_time_nsk = datetime.now(NSK_TZ)
    self.update_state(
        state=TASK_STATE_PROGRESS,
        meta={"received": 0, "downloaded": 0, "start_time": start_time_nsk.isoformat()},
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_run_download(self, start_time_nsk))
    finally:
        loop.close()
    return {"files_downloaded": result, "start_time": start_time_nsk.isoformat()}


async def _run_download(task: Task, start_time: datetime) -> int:
    async with async_session_factory() as session:
        uow = UnitOfWork(session)
        candidate_id = "candidate-" + str(uuid.uuid4())
        service = DownloadService(uow, candidate_id)

        async def progress_callback(received: int, downloaded: int) -> None:
            task.update_state(
                state=TASK_STATE_PROGRESS,
                meta={
                    "received": received,
                    "downloaded": downloaded,
                    "start_time": start_time.isoformat(),
                },
            )

        await service.run(progress_callback=progress_callback)
        await uow.commit()
        count = await uow.files.count_downloaded()
        logger.info("Download completed, total files: %d", count)
        return count
