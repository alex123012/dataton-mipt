from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import cv2
from celery import Celery

import notificators
import predictors
import settings
import video_parsers
from api_models.crud import get_user
from api_models.database import SessionLocal
from api_models.models import NotificatorType, Predictor
from api_models.models import Stream as ModelStream
from api_models.models import VideoParser
from api_models.schemas import Stream as SchemaStream


if TYPE_CHECKING:
    import numpy as np

celery_app = Celery("tasks", broker=str(settings.REDIS_URL), broker_connection_retry_on_startup=True)


predictors_map: dict[Predictor, type[predictors.AbstractPredictor]] = {
    Predictor.MOCK: predictors.MockPredictor,
    Predictor.BEACHGRABAGE: predictors.BeachGarbagePredictor,
}

video_parsers_map: dict[VideoParser, type[video_parsers.AbstractVideoParser]] = {
    VideoParser.YOUTUBE: video_parsers.YoutubeVideoParser,
}

notificators_map: dict[NotificatorType, type[notificators.AbstractNotificator]] = {
    NotificatorType.TELEGRAM: notificators.TelegramNotificator,
    NotificatorType.EMAIL: notificators.EmailNotificator,
}


@celery_app.task
def stream_with_notificators(stream_params: dict[str, Any]) -> None:
    try:
        stream = SchemaStream.model_validate(ModelStream(**stream_params))
    except ValueError:
        logging.exception("can't use stream_params to initialise Stream schema")
        return

    video_parser = video_parsers_map[stream.video_parser](stream.url)
    predictor = predictors_map[stream.predictor]()

    frame = video_parser.get_frame()
    if frame is None:
        logging.error("received None frame from video parser")
        return
    logging.info("received frame from video parser")

    logging.info("predicting results with predictor")
    predict = predictor.predict(frame, stream_name=stream.name, site_url=settings.SITE_URL)
    logging.info("predicted results with predictor")

    if not predict.result:
        logging.info("no predicted result from predictor")
        return

    user = get_user(SessionLocal(), stream.user_id)
    if not user:
        return

    image = numpy_to_binary(predict.image)
    for notificator in user.notificators:
        notificators_map[notificator.kind](**notificator.settings).send_notification(
            predict.message.message,
            image,
            parse_mode=predict.message.content_type,
        )


# Convert the numpy array to a binary object in memory
def numpy_to_binary(arr: np.ndarray) -> bytes:
    _, buffer = cv2.imencode(".jpg", arr)
    return buffer.tobytes()
