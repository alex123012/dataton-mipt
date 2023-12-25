from __future__ import annotations

import html
import logging
from typing import Literal, Self

import requests

from .abstract import AbstractNotificator


TELEGRAM_MAX_CAPTION_LEN = 1024


class TelegramNotificator(AbstractNotificator):
    def __init__(self: Self, chat_id: str, token: str) -> None:
        self.__chat_id = chat_id
        self.__token = token

    def send_notification(self: Self, message: str, image: bytes, parse_mode: Literal["html", "markdown"]) -> None:
        if len(message) > TELEGRAM_MAX_CAPTION_LEN:
            message = message[:1021] + "..."

        data = {
            "chat_id": self.__chat_id,
            "parse_mode": parse_mode.capitalize() if parse_mode == "markdown" else parse_mode,
            "caption": html.escape(message) if parse_mode != "html" else message,
        }

        files = {
            "photo": image,
        }

        bot_url = f"https://api.telegram.org/bot{self.__token}/sendPhoto"
        logging.info("sending notification to Telegram with data: %s", data)
        with requests.post(bot_url, data=data, files=files, timeout=5) as resp:
            if resp.ok:
                return

            logging.error("error sending telegram notification:\n%s", resp.text)
