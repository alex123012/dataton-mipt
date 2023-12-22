from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncGenerator, Self


if TYPE_CHECKING:
    import numpy as np


class AbstractVideoParser(ABC):
    @abstractmethod
    def start(self: Self) -> AsyncGenerator[np.ndarray, None]:
        pass

    @abstractmethod
    def stop(self: Self) -> None:
        pass
