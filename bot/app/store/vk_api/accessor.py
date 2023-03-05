import random
import typing
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Update
from app.web.utils import vk_make_update_from_raw, KeyboardHelper

if typing.TYPE_CHECKING:
    from bot_app.app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def send_message(self, chat_id: int, message: str) -> None:
        print(message)
        params = {
            "random_id": random.randint(1, 2**32),
            "peer_id": chat_id,
            "message": message,
            "access_token": self.app.config.bot.vk_token,
            "keyboard": KeyboardHelper.generate_helping_keyboard(),
        }
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params=params,
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def delete_message(self, chat, message_id):
        pass  # VK API is mostly for tests, no need to clear chat
