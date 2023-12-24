from __future__ import annotations

import logging
from typing import Any

from celery import Celery

import settings
from model.crud import get_user
from model.database import SessionLocal
from model.models import NotificatorType, Predictor
from model.models import Stream as ModelStream
from model.models import VideoParser
from model.schemas import Stream as SchemaStream
from notificator import AbstractNotificator, TelegramNotificator
from predictor import AbstractPredictor, MockPredictor
from video_parser import AbstractVideoParser, YoutubeVideoParser


celery_app = Celery("tasks", broker=str(settings.REDIS_URL), broker_connection_retry_on_startup=True)


def load_video_parser(name: VideoParser, url: str) -> AbstractVideoParser:
    if name == VideoParser.YOUTUBE:
        return YoutubeVideoParser(url)
    raise ValueError(f"Not supported parser: {name}")


def load_notificator(name: NotificatorType, settings: dict[str, str]) -> AbstractNotificator:
    if name == NotificatorType.TELEGRAM:
        return TelegramNotificator(**settings)
    raise ValueError(f"Not supported notificator: {name}")


mock_predictor = MockPredictor()


def load_predictor(name: Predictor) -> AbstractPredictor:
    if name == Predictor.MOCK:
        return mock_predictor
    raise ValueError(f"Not supported predictor: {name}")


@celery_app.task
def stream_with_notificators(stream_params: dict[str, Any]) -> None:
    try:
        stream = SchemaStream.model_validate(ModelStream(**stream_params))
    except ValueError:
        logging.exception("can't use stream_params to initialise Stream schema")
        return

    predictor = load_predictor(stream.predictor)
    video_parser = load_video_parser(stream.video_parser, stream.url)

    predict = predictor.predict(video_parser.get_frame(), parser_name=stream.name)
    if not predict.result:
        return

    user = get_user(SessionLocal(), stream.user_id)
    if not user:
        return

    for notificator in user.notificators:
        load_notificator(notificator.kind, notificator.settings).send_notification(predict.message)
