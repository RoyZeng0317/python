"""專注時鐘：顯示目前時間，並管理單一進度的專注計時（預設 2 小時）。"""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class FocusSession:
    stage_id: int
    duration_minutes: int
    start_time: datetime.datetime
    end_time: datetime.datetime

    def remaining_seconds(self, now: Optional[datetime.datetime] = None) -> int:
        now = now or datetime.datetime.now()
        return max(0, int((self.end_time - now).total_seconds()))

    def is_finished(self, now: Optional[datetime.datetime] = None) -> bool:
        return self.remaining_seconds(now) <= 0


class FocusClock:
    """管理目前時間顯示，以及對應每個學習進度的專注計時器。"""

    def __init__(self) -> None:
        self._session: Optional[FocusSession] = None

    @staticmethod
    def now() -> str:
        return datetime.datetime.now().isoformat(timespec="seconds")

    def start(self, stage_id: int, duration_minutes: int = 120) -> FocusSession:
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
        self._session = FocusSession(stage_id, duration_minutes, start_time, end_time)
        return self._session

    def stop(self) -> None:
        self._session = None

    @property
    def session(self) -> Optional[FocusSession]:
        return self._session
