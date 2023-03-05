from typing import Optional

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.store.tg_api.poller import Poller


class TGApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.API_PATH = "https://api.telegram.org/bot" + self.app.config.bot.tg_token
        self.session: Optional[ClientSession] = None
        self.poller: Optional[Poller] = None
        self.key: Optional[str] = None
        self.offset: Optional[int] = 1

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    async def poll(self):
        query = self._build_query(
                api_path=self.API_PATH,
                method="/getUpdates",
                params={
                    "offset": self.offset,
                    "timeout": 12,
                },
            )
        async with self.session.get(
                query
        ) as resp:
            data = await resp.json()
            self.offset = data[-1]["id"]
            b_data = await resp.read()
            await self.app.store.rabbit_accessor.send_to_queue(b_data)

    async def send_message(self, chat_id, message):
        query = self._build_query(
            api_path=self.API_PATH,
            method="/sendMessage",
            params={
                "chat_id": chat_id,
                "text": message,
            },
        )
        async with self.session.get(query) as resp:
            data = await resp.json()
            if data["ok"]:
                self.logger.info("message's sent to tg chat")
            return None

    @staticmethod
    def _build_query(api_path: str, method: str, params: dict) -> str:
        url = api_path + method + "?"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def delete_message(self, chat_id, message_id):
        query = self._build_query(
            api_path=self.API_PATH,
            method="/deleteMessage",
            params={
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )
        async with self.session.get(query) as resp:
            data = await resp.json()
            if data["ok"]:
                self.logger.info("message's deleted")
            return None
