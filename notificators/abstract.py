from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, Self


class AbstractNotificator(ABC):
    @abstractmethod
    def send_notification(self: Self, message: str, image: bytes, parse_mode: Literal["markdown", "html"]) -> None:
        pass
