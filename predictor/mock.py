from __future__ import annotations

from typing import TYPE_CHECKING, Self

from .abstract import AbstractPredictor, Predict


if TYPE_CHECKING:
    import numpy as np


class MockPredictor(AbstractPredictor):
    def predict(self: Self, _: np.ndarray, parser_name: str) -> Predict:
        return Predict(True, f"send my notification for {parser_name} parser!")
