import os
from pathlib import Path

from pydantic.v1 import BaseSettings


def _load_dotenv(path: Path) -> None:
    """
    Простой загрузчик `.env` без внешних зависимостей.

    Поддерживает строки вида KEY=VALUE, игнорирует пустые строки и комментарии (# ...).
    """
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class Settings(BaseSettings):
    rss_feed_url: str
    telegram_bot_token: str
    telegram_chat_id: str
    poll_interval_seconds: int
    database_url: str

_load_dotenv(Path(".env"))
settings = Settings()

