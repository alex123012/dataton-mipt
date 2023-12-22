from __future__ import annotations

import asyncio
import logging
import signal
import sys
from typing import TYPE_CHECKING, Any

from async_queue import Queue, TaskDefinition
from config import Notificator, Predictor, VideoParser, load_config
from notificator import AbstractNotificator, TelegramNotificator
from predictor import AbstractPredictor, MockPredictor
from video_parser import AbstractVideoParser, YoutubeVideoParser


if TYPE_CHECKING:
    from types import FrameType


logging.basicConfig(
    style="{",
    level=logging.DEBUG,
)


def load_parser(name: VideoParser, url: str) -> AbstractVideoParser:
    if name == VideoParser.YOUTUBE:
        return YoutubeVideoParser(url)
    raise ValueError(f"Not supported parser: {name}")


def load_notificator(name: Notificator, settings: dict[str, Any]) -> AbstractNotificator:
    if name == Notificator.TELEGRAM:
        return TelegramNotificator(**settings)
    raise ValueError(f"Not supported notificator: {name}")


def load_predictor(name: Predictor) -> AbstractPredictor:
    if name == Predictor.MOCK:
        return MockPredictor()
    raise ValueError(f"Not supported predictor: {name}")


def producer_definitions(parsers: dict[str, AbstractVideoParser], predictor: AbstractPredictor) -> list[TaskDefinition]:
    async def producer(queue: asyncio.Queue, name: str, parser: AbstractVideoParser, lock: asyncio.Lock) -> None:
        for frame in parser.start():
            async with lock:
                predict = predictor.predict(frame, name)
            if not predict.result:
                return

            await queue.put(predict.message)
            await asyncio.sleep(0.5)

    predictor_lock = asyncio.Lock()
    return [(producer, [name, parser, predictor_lock], {}) for name, parser in parsers.items()]


def consumer_definitions(notificators: list[AbstractNotificator]) -> list[TaskDefinition]:
    async def consumer(queue: asyncio.Queue, notificator: AbstractNotificator) -> None:
        while True:
            message = await queue.get()
            notificator.send_notification(message)
            queue.task_done()

    return [(consumer, [notificator], {}) for notificator in notificators]


def main() -> None:
    config = load_config(sys.argv[1])
    parsers = {stream.name: load_parser(stream.video_parser, stream.url) for stream in config.streams}
    notificators = [load_notificator(s.name, s.settings) for s in config.notificators]
    predictor = load_predictor(config.predictor)

    def exit_handler(_: int = 0, __: FrameType | None = None) -> None:
        logging.info("Exiting...")
        for parser in parsers.values():
            parser.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, exit_handler)

    queue = Queue(
        producer_definitions=producer_definitions(parsers, predictor),
        consumer_definitions=consumer_definitions(notificators),
    )
    asyncio.run(queue.start())

    exit_handler()


if __name__ == "__main__":
    main()
