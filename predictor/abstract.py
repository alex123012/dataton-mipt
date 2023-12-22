from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    import numpy as np


@dataclass
class Predict:
    result: bool
    message: str


class AbstractPredictor(ABC):
    @abstractmethod
    def predict(self: Self, frame: np.ndarray, parser_name: str) -> Predict:
        pass
