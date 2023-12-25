from __future__ import annotations

from typing import TYPE_CHECKING, Self

from .abstract import AbstractPredictor, Message, Predict


if TYPE_CHECKING:
    import numpy as np


class MockPredictor(AbstractPredictor):
    def predict(self: Self, frame: np.ndarray, stream_name: str, site_url: str) -> Predict:
        return Predict(
            True,
            Message(f'send my notification from <a href="{site_url}">site</a> for {stream_name} parser!', "html"),
            frame,
        )
