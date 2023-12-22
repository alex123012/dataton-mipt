from __future__ import annotations

import enum
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict


class YamlModel(BaseModel):
    model_config = ConfigDict()  # (alias_generator=to_camel)


class Config(YamlModel):
    predictor: Predictor
    streams: list[Stream]
    notificators: list[NotificatorSettings]


class Stream(YamlModel):
    url: str
    name: str
    video_parser: VideoParser


class NotificatorSettings(YamlModel):
    name: Notificator
    settings: dict[str, Any]


class Notificator(enum.Enum):
    Telegram = "Telegram"


class Predictor(enum.Enum):
    Mock = "Mock"


class VideoParser(enum.Enum):
    Youtube = "Youtube"


def load_config(path: str) -> Config:
    with Path(path).open() as f:
        contents = yaml.safe_load(f)
    return Config.model_validate_json(json.dumps(contents))
