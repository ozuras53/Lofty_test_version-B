import json
import ssl
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib import request

from .models import PostOut


class Notifier:
    """
    Отвечает за отправку уведомлений в Telegram.
    """

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self._base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self._ssl_context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")

    def notify(self, posts: Iterable[PostOut]) -> None:
        """
        Отправить уведомления о новых постах.
        """
        if not self.chat_id:
            print("[Notifier] TELEGRAM_CHAT_ID не задан. Пропускаю отправку.")
            return

        for post in posts:
            text = f"Новый пост:\n{post.title}\n{post.link}"
            self._send_message(text=text)

    def _send_message(self, text: str) -> None:
        payload = json.dumps(
            {
                "chat_id": self.chat_id,
                "text": text,
                "disable_web_page_preview": False,
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self._base_url}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15, context=self._ssl_context) as response:
                body = response.read().decode("utf-8")
            self._handle_success(body=body)
            return
        except HTTPError as exc:
            self._handle_http_error(exc)
            return
        except URLError as exc:
            print(f"[Notifier] Ошибка сети Telegram API: {exc}")
        except Exception as exc:
            print(f"[Notifier] Ошибка Telegram API: {exc}")
    
    def _handle_success(self, body: str) -> None:
        print(f"[Notifier] Сообщение отправлено в чат {self.chat_id}")
        if '"ok":true' not in body.replace(" ", ""):
            print(f"[Notifier] Неожиданный ответ Telegram API: {body}")

    @staticmethod
    def _handle_http_error(exc: HTTPError) -> None:
        response_body = ""
        try:
            response_body = exc.read().decode("utf-8")
        except Exception:
            pass
        print(f"[Notifier] HTTP ошибка Telegram API: {exc.code} {exc.reason}")
        if response_body:
            print(f"[Notifier] Тело ответа: {response_body}")
            if "chat not found" in response_body.lower():
                print("[Notifier] TELEGRAM_CHAT_ID неверный или боту не писали первым.")

