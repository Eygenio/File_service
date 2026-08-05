from datetime import datetime

from pydantic import BaseModel


class FileItemResponse(BaseModel):
    id: int
    name: str
    downloaded_at: datetime | None
    is_downloaded: bool


class StatsRequest(BaseModel):
    file_ids: list[int]


class StatsResponse(BaseModel):
    global_stats: dict[str, int]
    per_file_stats: dict[str, dict[str, int]]
