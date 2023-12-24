from __future__ import annotations

import html
import logging
from typing import Self

import requests

from .abstract import AbstractNotificator


class TelegramNotificator(AbstractNotificator):
    def __init__(self: Self, chat_id: str, token: str) -> None:
        self.chat_id = chat_id
        self.token = token

    def send_notification(self: Self, message: str) -> None:
        data = {
            "chat_id": self.chat_id,
            "text": html.escape(message),
            "parse_mode": "html",
        }

        bot_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        logging.info("sending notification to Telegram with data: %s", data)
        with requests.post(bot_url, data=data, timeout=5) as resp:
            if resp.ok:
                return

            logging.error("error sending telegram notification:\n%s", resp.text)
