from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, Self


if TYPE_CHECKING:
    import numpy as np


class AbstractVideoParser(ABC):
    @abstractmethod
    def start(self: Self) -> Generator[np.ndarray, None, None]:
        pass

    @abstractmethod
    def stop(self: Self) -> None:
        pass
