from abc import ABC, abstractmethod

from src.domain.entities import FileRecord


class IFileRepository(ABC):
    @abstractmethod
    async def add_or_update(self, record: FileRecord) -> FileRecord:
        pass

    @abstractmethod
    async def get_all(self, offset: int, limit: int) -> list[FileRecord]:
        pass

    @abstractmethod
    async def get_downloaded(self) -> list[FileRecord]:
        pass

    @abstractmethod
    async def get_by_names(self, names: list[str]) -> list[FileRecord]:
        pass

    @abstractmethod
    async def get_by_ids(self, ids: list[int]) -> list[FileRecord]:
        pass

    @abstractmethod
    async def count_downloaded(self) -> int:
        pass
