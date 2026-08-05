import asyncio
import logging
from io import BytesIO
from typing import Any
from zipfile import ZipFile

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
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
        timeout = aiohttp.ClientTimeout(total=60)
        self._session = aiohttp.ClientSession(
            headers=self._headers,
            timeout=timeout,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        assert self._session is not None
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._session.request(method, url, **kwargs)
                if response.status == status.HTTP_429_TOO_MANY_REQUESTS:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(
                        "Rate limited, retrying after %d seconds",
                        retry_after,
                    )
                    await asyncio.sleep(retry_after)
                    continue
                if response.status == status.HTTP_403_FORBIDDEN:
                    retry_after = int(response.headers.get("Retry-After", 1800))
                    logger.warning(
                        "Banned, waiting %d seconds before retry",
                        retry_after,
                    )
                    await asyncio.sleep(retry_after)
                    continue
                return response
            except (TimeoutError, ClientConnectionError) as e:
                logger.warning("Request failed on attempt %d: %s", attempt, e)
                if attempt == max_attempts:
                    raise
                await asyncio.sleep(2 ** (attempt - 1))
        raise RuntimeError("Max retries exceeded")

    async def _request_json(self, method: str, url: str, **kwargs: Any) -> Any:
        for attempt in range(3):
            response = await self._request(method, url, **kwargs)
            try:
                return await response.json()
            except (TimeoutError, ClientConnectionError) as e:
                logger.warning("JSON read failed on attempt %d: %s", attempt + 1, e)
                if attempt == 2:
                    raise
                await asyncio.sleep(2**attempt)
        raise RuntimeError("Max read retries exceeded")

    async def _request_bytes(self, method: str, url: str, **kwargs: Any) -> bytes:
        for attempt in range(3):
            response = await self._request(method, url, **kwargs)
            try:
                return await response.read()
            except (TimeoutError, ClientConnectionError) as e:
                logger.warning("Bytes read failed on attempt %d: %s", attempt + 1, e)
                if attempt == 2:
                    raise
                await asyncio.sleep(2**attempt)
        raise RuntimeError("Max read retries exceeded")

    async def get_file_names(self) -> list[str]:
        data: dict = await self._request_json(GET, f"{self._base_url}/api/files/names")
        return list(data["file_names"])

    async def download_files(self, file_names: list[str]) -> dict[str, str]:
        zip_bytes = await self._request_bytes(
            POST,
            f"{self._base_url}/api/files/download",
            json={"file_names": file_names},
        )
        return self._extract_zip(zip_bytes)

    async def mark_downloaded(self, file_names: list[str]) -> None:
        data: dict = await self._request_json(
            POST,
            f"{self._base_url}/api/files/downloaded",
            json={"file_names": file_names},
        )
        logger.info(
            "Successfully marked %d files as downloaded (marked_now=%d, already_marked=%d)",
            len(file_names),
            data.get("marked_now", 0),
            data.get("already_marked", 0),
        )

    @staticmethod
    def _extract_zip(zip_bytes: bytes) -> dict[str, str]:
        result: dict[str, str] = {}
        with ZipFile(BytesIO(zip_bytes)) as zip_file:
            for name in zip_file.namelist():
                with zip_file.open(name) as f:
                    result[name] = f.read().decode("utf-8")
        return result
