from collections import Counter

from src.infrastructure.unit_of_work import UnitOfWork


class StatsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def calculate_stats(self, file_ids: list[int]) -> dict:
        files = await self.uow.files.get_by_ids(file_ids)
        global_counter: Counter[str] = Counter()
        per_file_stats: dict[str, dict[str, int]] = {}

        for file in files:
            if file.content is not None:
                counter = Counter(file.content)
                global_counter += counter
                per_file_stats[file.name] = dict(counter)

        return {
            "global_stats": dict(global_counter),
            "per_file_stats": per_file_stats,
        }
