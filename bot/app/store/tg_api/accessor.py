from typing import Optional

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor


class TGApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.API_PATH = "https://api.telegram.org/bot" + self.app.config.bot.tg_token
        self.session: Optional[ClientSession] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()

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
