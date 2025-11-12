from itertools import cycle
from typing import Iterable, Optional


class AssignmentService:
    def __init__(self, collectors: Iterable[str]) -> None:
        collector_list = list(collectors)
        if not collector_list:
            collector_list = ['unassigned']
        self._ring = cycle(collector_list)

    def pick(self, preferred: Optional[str] = None) -> str:
        if preferred:
            return preferred
        return next(self._ring)
