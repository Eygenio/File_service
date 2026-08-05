from pydantic import BaseModel


class AppConfig(BaseModel):
    title: str = "File Downloader & Analyzer"
    version: str = "1.0.0"
    description: str = "Service for downloading and analyzing text files"
    host: str
    port: int
