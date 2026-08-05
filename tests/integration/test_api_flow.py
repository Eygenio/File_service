from unittest.mock import MagicMock

import pytest
from fastapi import status
from starlette.testclient import TestClient

from src.domain.entities import FileRecord


@pytest.mark.integration
def test_files_to_stats_flow(api_client: TestClient, mock_uow: MagicMock) -> None:
    mock_uow.files.get_all.return_value = [
        FileRecord(id=1, name="first.txt", is_downloaded=True, content="00"),
        FileRecord(id=2, name="second.txt", is_downloaded=True, content="11"),
    ]
    mock_uow.files.get_by_ids.return_value = mock_uow.files.get_all.return_value
    mock_uow.files.count_downloaded.return_value = 2

    resp = api_client.get("/api/files?page=1")
    assert resp.status_code == status.HTTP_200_OK
    files = resp.json()
    assert len(files) == 2

    file_ids = [f["id"] for f in files]
    resp = api_client.post("/api/stats", json={"file_ids": file_ids})
    assert resp.status_code == status.HTTP_200_OK
    stats = resp.json()
    assert stats["global_stats"]["0"] == 2
    assert stats["global_stats"]["1"] == 2
