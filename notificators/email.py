from __future__ import annotations

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Literal, Self

from markdown import markdown

import settings

from .abstract import AbstractNotificator


class EmailNotificator(AbstractNotificator):
    __sender_email = settings.SMTP_EMAIL
    __sender_password = str(settings.SMTP_PASSWORD)
    __host_sender = __sender_email.split("@")[1]

    def __init__(self: Self, email_getter: str) -> None:
        self.__email_getter = email_getter

    def send_notification(self: Self, message: str, image: bytes, parse_mode: Literal["html", "markdown"]) -> None:
        msg = MIMEMultipart()
        msg["Subject"] = "Important notification from CBA on Beach Condition"
        msg["From"] = self.__sender_email
        msg["To"] = self.__email_getter
        msg.attach(MIMEText((message if parse_mode == "html" else markdown(message)), "html"))
        msg.attach(MIMEImage(image, name="stream-image.jpg"))

        with smtplib.SMTP_SSL(f"smtp.{self.__host_sender}", 465) as smtp_server:
            smtp_server.login(self.__sender_email, self.__sender_password)
            smtp_server.sendmail(self.__sender_email, self.__email_getter, msg.as_string())

            smtp_server.quit()
