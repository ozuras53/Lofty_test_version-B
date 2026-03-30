import hashlib
import ssl
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List
from urllib.error import URLError
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from .models import PostIn


class RSSParser:
    """
    Отвечает за получение и парсинг RSS-ленты в объекты PostIn.
    """

    def __init__(self, feed_url: str) -> None:
        self.feed_url = feed_url
        self._ssl_context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")

    def fetch_and_parse(self) -> List[PostIn]:
        """
        Получить RSS-ленту и преобразовать элементы в модели PostIn.
        """
        print(f"[RSSParser] Получаю RSS-ленту: {self.feed_url}")
        try:
            with urlopen(self.feed_url, timeout=20, context=self._ssl_context) as response:
                raw = response.read()
            root = ET.fromstring(raw)
        except URLError as exc:
            print(f"[RSSParser] Ошибка сети при чтении RSS: {exc}")
            return []
        except ET.ParseError as exc:
            print(f"[RSSParser] Ошибка разбора RSS XML: {exc}")
            return []

        channel = root.find("channel")
        posts: List[PostIn] = []

        if channel is None:
            print("[RSSParser] В ленте не найден элемент channel")
            return posts

        for item in channel.findall("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            published_raw = (item.findtext("pubDate") or "").strip()

            if not title or not link:
                continue

            published_at = self._parse_published_at(published_raw)
            content_hash = self._build_content_hash(title, link, description)

            posts.append(
                PostIn(
                    title=title,
                    link=link,
                    published_at=published_at,
                    content_hash=content_hash,
                )
            )

        print(f"[RSSParser] Получено постов: {len(posts)}")
        return posts

    @staticmethod
    def _parse_published_at(value: str) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        try:
            return parsedate_to_datetime(value).astimezone(timezone.utc)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)

    @staticmethod
    def _build_content_hash(title: str, link: str, description: str) -> str:
        raw = f"{title}|{link}|{description}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

