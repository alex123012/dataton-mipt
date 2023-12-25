from __future__ import annotations

import enum
from typing import ClassVar, Self

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    type_annotation_map: ClassVar = {dict[str, str]: JSON}


class Predictor(enum.Enum):
    MOCK = "Mock"
    BEACHGRABAGE = "Beach garbage"


class VideoParser(enum.Enum):
    YOUTUBE = "Youtube"


class Stream(Base):
    __tablename__ = "stream"
    name: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String)
    predictor: Mapped[Predictor] = mapped_column(Enum(Predictor))
    video_parser: Mapped[VideoParser] = mapped_column(Enum(VideoParser))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    time_created = mapped_column(DateTime(timezone=True), server_default=func.now())  # pylint:disable=E1102
    time_updated = mapped_column(DateTime(timezone=True), onupdate=func.now())  # pylint:disable=E1102

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True, index=True)
    user: Mapped[User] = relationship(back_populates="streams")

    def __repr__(self: Self) -> str:
        return f"Stream(name={self.name!r}, url={self.url!r}, predictor={self.predictor!r}, video_parser={self.video_parser!r}, is_active={self.is_active!r})"  # noqa:E501 pylint:disable=C0301

    def __str__(self: Self) -> str:
        return self.__repr__()


class NotificatorType(enum.Enum):
    TELEGRAM = "Telegram"
    EMAIL = "email"


class Notificator(Base):
    __tablename__ = "notificator"
    name: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    kind: Mapped[NotificatorType] = mapped_column(Enum(NotificatorType))
    settings: Mapped[dict[str, str]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    time_created = mapped_column(DateTime(timezone=True), server_default=func.now())  # pylint:disable=E1102
    time_updated = mapped_column(DateTime(timezone=True), onupdate=func.now())  # pylint:disable=E1102

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True, index=True)
    user: Mapped[User] = relationship(back_populates="notificators")

    def __repr__(self: Self) -> str:
        return f"Notificator(name={self.name!r}, kind={self.kind!r}, settings={self.settings!r},  is_active={self.is_active!r})"  # noqa: E501 pylint:disable=C0301

    def __str__(self: Self) -> str:
        return self.__repr__()


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    login: Mapped[str] = mapped_column(String)

    streams: Mapped[list[Stream]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notificators: Mapped[list[Notificator]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self: Self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, login={self.login!r})"

    def __str__(self: Self) -> str:
        return self.__repr__()
