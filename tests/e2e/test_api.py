from unittest.mock import MagicMock, patch

from fastapi import status
from starlette.testclient import TestClient

from src.application.constants import (
    API_STATUS_COMPLETED,
    API_STATUS_FAILED,
    API_STATUS_PENDING,
    API_STATUS_PROGRESS,
    TASK_STATE_FAILURE,
    TASK_STATE_PENDING,
    TASK_STATE_PROGRESS,
    TASK_STATE_SUCCESS,
)
from src.tasks.download_task import download_task


class TestHealthAndPages:
    def test_main_page_renders(self, api_client: TestClient) -> None:
        resp = api_client.get("/")
        assert resp.status_code == status.HTTP_200_OK
        assert "File Downloader" in resp.text

    def test_files_page_renders(self, api_client: TestClient) -> None:
        resp = api_client.get("/files")
        assert resp.status_code == status.HTTP_200_OK
        assert "Скачанные файлы" in resp.text


class TestDownloadAPI:
    @patch.object(download_task, "delay")
    def test_start_download(
        self,
        mock_delay: MagicMock,
        api_client: TestClient,
    ) -> None:
        mock_delay.return_value.id = "fake-task-id"
        resp = api_client.post("/api/download/start")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"task_id": "fake-task-id"}

    @patch.object(download_task, "AsyncResult")
    def test_download_status_pending(
        self, mock_async_result: MagicMock, api_client: TestClient
    ) -> None:
        mock_task = mock_async_result.return_value
        mock_task.state = TASK_STATE_PENDING

        resp = api_client.get("/api/download/status/task-123")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": API_STATUS_PENDING}

    @patch.object(download_task, "AsyncResult")
    def test_download_status_progress(
        self, mock_async_result: MagicMock, api_client: TestClient
    ) -> None:
        mock_task = mock_async_result.return_value
        mock_task.state = TASK_STATE_PROGRESS
        mock_task.info = {
            "received": 5,
            "downloaded": 3,
            "start_time": "2026-01-01T00:00:00",
        }

        resp = api_client.get("/api/download/status/task-123")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["status"] == API_STATUS_PROGRESS
        assert data["progress"]["received"] == 5
        assert data["progress"]["downloaded"] == 3

    @patch.object(download_task, "AsyncResult")
    def test_download_status_success(
        self,
        mock_async_result: MagicMock,
        api_client: TestClient,
    ) -> None:
        mock_task = mock_async_result.return_value
        mock_task.state = TASK_STATE_SUCCESS
        mock_task.result = {"files_downloaded": 42}

        resp = api_client.get("/api/download/status/task-123")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {
            "status": API_STATUS_COMPLETED,
            "result": {"files_downloaded": 42},
        }

    @patch.object(download_task, "AsyncResult")
    def test_download_status_failure(
        self,
        mock_async_result: MagicMock,
        api_client: TestClient,
    ) -> None:
        mock_task = mock_async_result.return_value
        mock_task.state = TASK_STATE_FAILURE
        mock_task.info = Exception("Something went wrong")

        resp = api_client.get("/api/download/status/task-123")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {
            "status": API_STATUS_FAILED,
            "error": "Something went wrong",
        }


class TestFilesAPI:
    def test_get_files(
        self,
        api_client: TestClient,
        mock_uow: MagicMock,
    ) -> None:
        mock_uow.files.get_all.return_value = [
            type(
                "File",
                (),
                {
                    "id": 1,
                    "name": "a.txt",
                    "downloaded_at": None,
                    "is_downloaded": True,
                },
            ),
            type(
                "File",
                (),
                {
                    "id": 2,
                    "name": "b.txt",
                    "downloaded_at": None,
                    "is_downloaded": True,
                },
            ),
        ]

        resp = api_client.get("/api/files?page=1")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data) == 2
        assert data[0]["name"] == "a.txt"

    def test_get_files_count(
        self,
        api_client: TestClient,
        mock_uow: MagicMock,
    ) -> None:
        mock_uow.files.count_downloaded.return_value = 10

        resp = api_client.get("/api/files/count")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"total": 10}

    def test_calculate_stats(
        self,
        api_client: TestClient,
        mock_uow: MagicMock,
    ) -> None:
        from src.domain.entities import FileRecord

        mock_uow.files.get_by_ids.return_value = [
            FileRecord(id=1, name="f1.txt", content="12", is_downloaded=True),
            FileRecord(id=2, name="f2.txt", content="22", is_downloaded=True),
        ]

        resp = api_client.post("/api/stats", json={"file_ids": [1, 2]})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["global_stats"] == {"1": 1, "2": 3}
        assert data["per_file_stats"]["f1.txt"]["1"] == 1
        assert data["per_file_stats"]["f2.txt"]["2"] == 2
