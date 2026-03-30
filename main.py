import asyncio

from app.config import settings
from app.scheduler import Scheduler


async def main() -> None:
    """
    Точка входа для приложения RSS → Telegram.
    """
    print("[Main] Запуск приложения")
    print(f"[Main] RSS-лента: {settings.rss_feed_url}")
    scheduler = Scheduler()
    await scheduler.run_forever()


if __name__ == "__main__":
    asyncio.run(main())

