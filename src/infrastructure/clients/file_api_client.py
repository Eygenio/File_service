import asyncio
import logging
from io import BytesIO
from typing import Any
from zipfile import ZipFile

import aiohttp
from fastapi import status

from src.application.constants import GET, POST
from src.config.settings import settings

logger = logging.getLogger(__name__)


class FileApiClient:
    def __init__(
        self,
        candidate_id: str,
        base_url: str = settings.external_api_base_url,
    ) -> None:
        self._candidate_id = candidate_id
        self._base_url = base_url
        self._session: aiohttp.ClientSession | None = None
        self._headers = {"X-Candidate-Id": candidate_id}

    async def __aenter__(self) -> "FileApiClient":
        self._session = aiohttp.ClientSession(headers=self._headers)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    async def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> Any:
        while True:
            async with self._session.request(method, url, **kwargs) as response:  # type: ignore[union-attr]
                if response.status == status.HTTP_429_TOO_MANY_REQUESTS:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning("Rate limited, retrying after %d seconds", retry_after)
                    await asyncio.sleep(retry_after)
                    continue
                if response.status == status.HTTP_403_FORBIDDEN:
                    retry_after = int(response.headers.get("Retry-After", 1800))
                    logger.error("Banned for %d seconds", retry_after)
                    raise Exception(f"Banned for {retry_after} seconds")
                return response

    async def get_file_names(self) -> list[str]:
        response = await self._request_with_retry(GET, f"{self._base_url}/api/files/names")
        data: dict = await response.json()
        file_names: list[str] = data["file_names"]
        return file_names

    async def download_files(self, file_names: list[str]) -> dict[str, str]:
        response = await self._request_with_retry(
            POST,
            f"{self._base_url}/api/files/download",
            json={"file_names": file_names},
        )
        zip_bytes = await response.read()
        return self._extract_zip(zip_bytes)

    async def mark_downloaded(self, file_names: list[str]) -> None:
        await self._request_with_retry(
            POST,
            f"{self._base_url}/api/files/downloaded",
            json={"file_names": file_names},
        )

    @staticmethod
    def _extract_zip(zip_bytes: bytes) -> dict[str, str]:
        result: dict[str, str] = {}
        with ZipFile(BytesIO(zip_bytes)) as zip_file:
            for name in zip_file.namelist():
                with zip_file.open(name) as f:
                    result[name] = f.read().decode("utf-8")
        return result
