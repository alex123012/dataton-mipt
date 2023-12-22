from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Self

from vidgear.gears import CamGear

from .abstract import AbstractVideoParser


if TYPE_CHECKING:
    import numpy as np


class YoutubeVideoParser(AbstractVideoParser):
    def __init__(self: Self, stream_url: str, delay_secs: int = 60) -> None:
        self.__cam_gear = CamGear(
            source=stream_url,
            stream_mode=True,
            time_delay=1,
            logging=True,
            STREAM_RESOLUTION="720p",
            CAP_PROP_FPS=30,
            STREAM_PARAMS={
                "nocheckcertificate": True,
                "external_downloader_args": "ffmpeg:-http_persistent 0",
            },
        )

        self.frame_delay = delay_secs * 30

    def start(self: Self) -> Generator[np.ndarray, None, None]:
        self.__stream = self.__cam_gear.start()
        currentframe = self.frame_delay - 1
        while True:
            frame = self.__stream.read()
            if frame is None:
                break

            currentframe += 1
            if currentframe % self.frame_delay != 0:
                continue

            currentframe = 0
            yield frame

    def stop(self: Self) -> None:
        self.__cam_gear.stop()
        if hasattr(self, "_YoutubeVideoParser__stream"):
            self.__stream.stop()
