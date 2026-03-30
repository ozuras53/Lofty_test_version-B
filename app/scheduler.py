import asyncio
from typing import Optional

from .config import settings
from .notifier import Notifier
from .parser import RSSParser
from .storage import Storage


class Scheduler:
    """
    Периодически опрашивает RSS-ленту и запускает сохранение + уведомление.
    """

    def __init__(
        self,
        parser: Optional[RSSParser] = None,
        storage: Optional[Storage] = None,
        notifier: Optional[Notifier] = None,
    ) -> None:
        self.parser = parser or RSSParser(feed_url=str(settings.rss_feed_url))
        self.storage = storage or Storage()
        self.notifier = notifier or Notifier(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
        )
        self._interval = settings.poll_interval_seconds

    async def run_once(self) -> None:
        """
        Выполнить один цикл опроса.
        """
        print("[Scheduler] Выполняю один цикл опроса")
        posts = self.parser.fetch_and_parse()
        new_posts = self.storage.save_new_posts(posts)
        self.notifier.notify(new_posts)

    async def run_forever(self) -> None:
        """
        Бесконечный цикл опроса с паузой между итерациями.
        """
        print(f"[Scheduler] Запускаю цикл с интервалом {self._interval}с")
        while True:
            await self.run_once()
            await asyncio.sleep(self._interval)

