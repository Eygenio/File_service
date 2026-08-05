from datetime import datetime

from pydantic import BaseModel


class FileRecord(BaseModel):
    id: int | None = None
    name: str
    content: str | None = None
    downloaded_at: datetime | None = None
    is_downloaded: bool = False
