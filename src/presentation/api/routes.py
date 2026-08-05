import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from src.application.constants import (
    API_STATUS_COMPLETED,
    API_STATUS_FAILED,
    API_STATUS_PENDING,
    API_STATUS_PROGRESS,
    LIMIT,
    OFFSET,
    TASK_STATE_FAILURE,
    TASK_STATE_PENDING,
    TASK_STATE_PROGRESS,
    TASK_STATE_SUCCESS,
)
from src.application.services.stats_service import StatsService
from src.presentation.dependencies import get_stats_service
from src.presentation.schemas.file_schemas import FileItemResponse, StatsRequest, StatsResponse
from src.tasks.download_task import download_task

logger = logging.getLogger(__name__)
router = APIRouter()


env = Environment(loader=FileSystemLoader("src/presentation/templates"), auto_reload=True)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Any:
    template = env.get_template("index.html")
    return HTMLResponse(content=template.render(request=request))


@router.get("/files", response_class=HTMLResponse)
async def files_page(request: Request) -> Any:
    template = env.get_template("files.html")
    return HTMLResponse(content=template.render(request=request))


@router.post("/api/download/start")
async def start_download() -> dict[str, str]:
    task = download_task.delay()
    return {"task_id": task.id}


@router.get("/api/download/status/{task_id}")
async def download_status(task_id: str) -> dict[str, Any]:
    task = download_task.AsyncResult(task_id)
    if task.state == TASK_STATE_PENDING:
        return {"status": API_STATUS_PENDING}
    elif task.state == TASK_STATE_PROGRESS:
        return {"status": API_STATUS_PROGRESS, "progress": task.info}
    elif task.state == TASK_STATE_SUCCESS:
        return {"status": API_STATUS_COMPLETED, "result": task.result}
    elif task.state == TASK_STATE_FAILURE:
        return {"status": API_STATUS_FAILED, "error": str(task.info)}
    return {"status": task.state}


@router.get("/api/files", response_model=list[FileItemResponse])
async def get_files(
    page: int = Query(1, ge=1),
    stats_service: StatsService = Depends(get_stats_service),
) -> list[FileItemResponse]:
    files = await stats_service.uow.files.get_all(offset=(page - OFFSET) * LIMIT, limit=LIMIT)
    result = []
    for file in files:
        assert file.id is not None
        result.append(
            FileItemResponse(
                id=file.id,
                name=file.name,
                downloaded_at=file.downloaded_at,
                is_downloaded=file.is_downloaded,
            )
        )
    return result


@router.get("/api/files/count")
async def get_total_files(stats_service: StatsService = Depends(get_stats_service)) -> dict:
    count = await stats_service.uow.files.count_downloaded()
    return {"total": count}


@router.post("/api/stats", response_model=StatsResponse)
async def calculate_stats(
    request: StatsRequest,
    stats_service: StatsService = Depends(get_stats_service),
) -> StatsResponse:
    result = await stats_service.calculate_stats(request.file_ids)
    return StatsResponse(**result)
