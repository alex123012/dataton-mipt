from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    import numpy as np


class AbstractVideoParser(ABC):
    @abstractmethod
    def get_frame(self: Self) -> np.ndarray:
        pass
