from app.base.base_accessor import BaseAccessor


class TGApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.API_PATH = "https://api.telegram.org/bot" + self.app.config.bot.tg_token

    async def send_message(self, chat_id: int, message: str):
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

    async def delete_message(self, chat_id: int, message_id: int):
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
