from starlette.config import Config
from starlette.datastructures import Secret


config = Config(".env")


DATABASE_URL = config("DATABASE_URL", cast=Secret, default="postgresql://api:password@127.0.0.1:5432/api")
REDIS_URL = config("REDIS_URL", cast=Secret, default="redis://127.0.0.1:6379")
