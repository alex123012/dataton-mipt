from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self
from zoneinfo import ZoneInfo

import yolov5  # type:ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader

from .abstract import AbstractPredictor, Message, Predict


if TYPE_CHECKING:
    import numpy as np
    from torch import nn
    from yolov5.models import common, experimental  # type:ignore[import-untyped]


class BeachGarbagePredictor(AbstractPredictor):
    """Class for counting garbage in a beach video feed.

    Parameters
    ----------
        template(Pathlike): message template absolute file path.
    """

    __model: common.DetectMultiBackend | experimental.Ensemble | nn.Module | nn.ModuleList | common.AutoShape
    __threshold: int
    template: Path = Path(__file__).parent / "templates/beach.md"
    __template_content_type: Literal["markdown"] = "markdown"

    def __init__(  # noqa:PLR0913 pylint:disable=R0913
        self: Self,
        threshold: int = 3,
        conf: float = 0.3,
        iou: float = 0.5,
        agnostic: bool = False,
        multi_label: bool = False,
        max_det: int = 100,
    ) -> None:
        """Initialize the BeachGarbagePredictor with model parameters.

        Args:
        ----
            threshold (int): Threshold count to trigger alert.
            model_name (str): Model name for beach garbage collection detection.
            conf (float): Confidence threshold for the model.
            iou (float): Intersection over Union threshold for the model.
            agnostic (bool): Class-agnostic setting for the model.
            multi_label (bool): Multi-label setting for the model.
            max_det (int): Maximum number of detections per image.
        """
        # Set threshold for model score result
        self.__threshold = threshold

        # Load the garbage detection model
        self.__model = yolov5.load("keremberke/yolov5n-garbage")

        # Set model parameters
        self.__model.conf = conf  # Set NMS confidence threshold
        self.__model.iou = iou  # Set NMS IoU threshold
        self.__model.agnostic = agnostic  # Set NMS class-agnostic
        self.__model.multi_label = multi_label  # Set NMS multiple labels per box
        self.__model.max_det = max_det  # Set maximum number of detections per image

    def predict(self: Self, frame: np.ndarray, stream_name: str, site_url: str) -> Predict:
        predict, new_images = self.__model_predict(frame)
        message = self.__prepare_message(stream_name, site_url) if predict else ""

        return Predict(result=predict, message=Message(message, self.__template_content_type), image=new_images[0])

    def __model_predict(self: Self, frame: np.ndarray) -> tuple[bool, list[np.ndarray]]:
        results: common.Detections = self.__model(frame)
        predictions = results.pred[0]
        scores = predictions[:, 4]  # Confidence scores
        count = len(scores)  # Count of detected objects
        return count >= self.__threshold, results.render()

    def __prepare_message(self: Self, stream_name: str, site_url: str) -> str:
        # Load the current directory as template directory
        file_loader = FileSystemLoader(self.template.parent)
        # Create Environment object for template handling
        env = Environment(loader=file_loader, autoescape=True)

        # Load Markdown template
        template = env.get_template(str(self.template.name))

        # Data to replace in the template
        data = {
            "stream_name": stream_name,
            "date": datetime.now(ZoneInfo("Europe/Moscow")).strftime("%d %B %Y"),
            "site_url": site_url,
        }

        return template.render(data)


if __name__ == "__main__":
    import logging
    import os
    import sys

    import cv2

    from notificators import AbstractNotificator, EmailNotificator, TelegramNotificator

    image = cv2.imread(sys.argv[1])

    predictor = BeachGarbagePredictor(threshold=1)
    result = predictor.predict(image, "test", "http://localhost:8000")
    cv2.imwrite("tmp_result.jpg", result.image)
    if result.result:
        _, buffer = cv2.imencode(".jpg", result.image)
        result_image = buffer.tobytes()
        with Path("tmp_result_binary.jpg").open(mode="wb") as f:
            f.write(result_image)

        notifs: list[AbstractNotificator] = [
            TelegramNotificator(os.environ.get("TELEGRAM_CHAT_ID", ""), os.environ.get("TELEGRAM_TOKEN", "")),
            EmailNotificator("makhonin.a.ru@gmail.com"),
        ]
        for notif in notifs:
            try:
                notif.send_notification(result.message.message, result_image, "markdown")
            except Exception:  # noqa: PERF203 pylint:disable=W0702,W0718
                logging.exception("error sending meesage with %s", notif)
