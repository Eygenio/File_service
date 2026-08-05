from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.testclient import TestClient

from src.app import app
from src.application.services.stats_service import StatsService
from src.domain.entities import FileRecord
from src.domain.repositories import IFileRepository
from src.infrastructure.unit_of_work import UnitOfWork
from src.presentation.dependencies import get_uow


@pytest.fixture
def mock_files_repo() -> MagicMock:
    repo = AsyncMock(spec=IFileRepository)
    return repo


@pytest.fixture
def mock_uow(mock_files_repo: MagicMock) -> MagicMock:
    uow = MagicMock(spec=UnitOfWork)
    uow.files = mock_files_repo
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture(autouse=True)
def override_get_uow(mock_uow: MagicMock) -> Generator[None]:
    async def _override() -> AsyncGenerator[UnitOfWork]:
        yield mock_uow

    app.dependency_overrides[get_uow] = _override
    yield
    app.dependency_overrides.pop(get_uow, None)


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def stats_service(mock_uow: MagicMock) -> StatsService:
    return StatsService(mock_uow)


@pytest.fixture
def sample_file_record() -> FileRecord:
    return FileRecord(
        id=1,
        name="test.txt",
        content="123123",
        is_downloaded=True,
    )
