from __future__ import annotations

from fastapi import Form
from pydantic import BaseModel, ConfigDict

from .models import NotificatorType, Predictor, VideoParser


class StreamBase(BaseModel):
    name: str
    url: str
    predictor: Predictor
    video_parser: VideoParser


class StreamCreate(StreamBase):
    @classmethod
    def as_form(
        cls: type[StreamCreate],
        name: str = Form(),
        url: str = Form(),
        video_parser: str = Form(),
        predictor: str = Form(),
    ) -> StreamCreate:
        return cls(name=name, url=url, video_parser=VideoParser(video_parser), predictor=Predictor(predictor))


class Stream(StreamBase):
    model_config = ConfigDict(from_attributes=True)

    is_active: bool
    user_id: int


class NotificatorBase(BaseModel):
    name: str
    kind: NotificatorType
    settings: dict[str, str]


class NotificatorCreate(NotificatorBase):
    @classmethod
    def as_form(
        cls: type[NotificatorCreate],
        name: str = Form(),
        kind: str = Form(),
        settings: str = Form(),
    ) -> NotificatorCreate:
        settings_dict = {k.split("=")[0]: k.split("=")[1] for k in settings.split(",")}
        return cls(name=name, kind=NotificatorType(kind), settings=settings_dict)


class Notificator(NotificatorBase):
    model_config = ConfigDict(from_attributes=True)

    is_active: bool
    user_id: int


class UserBase(BaseModel):
    name: str
    login: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    streams: list[Stream]
    notificators: list[Notificator]
