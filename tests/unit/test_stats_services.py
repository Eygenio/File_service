from unittest.mock import MagicMock

import pytest

from src.application.services.stats_service import StatsService
from src.domain.entities import FileRecord


@pytest.mark.asyncio
async def test_calculate_stats_success(
    stats_service: StatsService,
    mock_uow: MagicMock,
    sample_file_record: FileRecord,
) -> None:
    mock_uow.files.get_by_ids.return_value = [sample_file_record]

    result = await stats_service.calculate_stats([1])

    assert result["global_stats"]["1"] == 2
    assert result["global_stats"]["2"] == 2
    assert result["global_stats"]["3"] == 2
    assert result["per_file_stats"]["test.txt"]["1"] == 2
    mock_uow.files.get_by_ids.assert_called_once_with([1])


@pytest.mark.asyncio
async def test_calculate_stats_empty_ids(
    stats_service: StatsService,
    mock_uow: MagicMock,
) -> None:
    mock_uow.files.get_by_ids.return_value = []

    result = await stats_service.calculate_stats([])

    assert result["global_stats"] == {}
    assert result["per_file_stats"] == {}


@pytest.mark.asyncio
async def test_calculate_stats_file_without_content(
    stats_service: StatsService,
    mock_uow: MagicMock,
) -> None:
    record = FileRecord(id=2, name="empty.txt", content=None, is_downloaded=True)
    mock_uow.files.get_by_ids.return_value = [record]

    result = await stats_service.calculate_stats([2])

    assert result["global_stats"] == {}
    assert result["per_file_stats"] == {}
