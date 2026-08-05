import logging

from celery import Celery

from src.config.settings import settings

logger = logging.getLogger(__name__)

celery = Celery(
    "worker",
    broker=settings.broker.url,
    backend=settings.broker.result_backend,
    include=["src.tasks.download_task"],
)

celery.conf.beat_schedule = {
    "download-files-every-hour": {
        "task": "src.tasks.download_task.download_task",
        "schedule": 3600.0,
    }
}
