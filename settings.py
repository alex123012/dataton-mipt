import logging

from starlette.config import Config
from starlette.datastructures import Secret


config = Config(".env")

logging.basicConfig(
    style="{",
    level=logging.DEBUG,
)

DATABASE_URL = config("DATABASE_URL", cast=Secret, default="postgresql://api:password@127.0.0.1:5432/api")
REDIS_URL = config("REDIS_URL", cast=Secret, default="redis://127.0.0.1:6379")

SITE_URL = config("SITE_URL", cast=str, default="http://127.0.0.1:8000")

SMTP_EMAIL = config("SMTP_EMAIL", cast=str, default="clean_beach_alert@mail.ru")
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=Secret, default="")
