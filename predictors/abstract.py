from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Self


if TYPE_CHECKING:
    import numpy as np


@dataclass
class Predict:
    result: bool
    message: Message
    image: np.ndarray


@dataclass
class Message:
    message: str
    content_type: Literal["markdown", "html"]


class AbstractPredictor(ABC):
    @abstractmethod
    def predict(self: Self, frame: np.ndarray, stream_name: str, site_url: str) -> Predict:
        pass
