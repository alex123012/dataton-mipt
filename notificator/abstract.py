from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


class AbstractNotificator(ABC):
    @abstractmethod
    def send_notification(self: Self, message: str) -> None:
        pass
