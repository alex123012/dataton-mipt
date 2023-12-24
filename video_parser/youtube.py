from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

from vidgear.gears import CamGear

from .abstract import AbstractVideoParser


if TYPE_CHECKING:
    import numpy as np


class YoutubeVideoParser(AbstractVideoParser):
    def __init__(self: Self, stream_url: str, delay_secs: int = 60) -> None:
        self.__cam_gear_params = {
            "source": stream_url,
            "stream_mode": True,
            "time_delay": 1,
            "logging": True,
            "STREAM_RESOLUTION": "720p",
            "CAP_PROP_FPS": 30,
            "STREAM_PARAMS": {
                "nocheckcertificate": True,
                "external_downloader_args": "ffmpeg:-http_persistent 0",
            },
        }

        self.frame_delay = delay_secs * 30

    def get_frame(self: Self) -> np.ndarray:
        __stream = CamGear(**self.__cam_gear_params).start()
        try:
            frame = __stream.read()
        except Exception:
            logging.exception("error reading frame")
        finally:
            __stream.stop()

        return frame
