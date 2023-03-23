from app.base.base_accessor import BaseAccessor

from app.web.utils import KeyboardHelper, _build_query


class TGApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.keyboard_helper = KeyboardHelper(external_api=app.config.bot.api)
        self.API_PATH = "https://api.telegram.org/bot" + self.app.config.bot.tg_token

    async def send_message(self, chat_id: int, message: str, **params):
        keyboard="[]"
        if "keyboard" not in params:
            keyboard = self.keyboard_helper.generate_helping_keyboard()
        else:
            if params["keyboard"] == 1:
                keyboard = self.keyboard_helper.generate_settings_keyboard()
        query = _build_query(
            host=self.API_PATH,
            method="/sendMessage",
            params={
                "chat_id": chat_id,
                "text": message,
                "reply_markup": keyboard
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
