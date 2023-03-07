import random
import typing

from app.base.base_accessor import BaseAccessor
from app.web.utils import vk_make_update_from_raw, KeyboardHelper, _build_query

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.API_PATH = "https://api.vk.com/method/"

    async def send_message(self, chat_id: int, message: str) -> None:
        params = {
            "random_id": random.randint(1, 2**32),
            "peer_id": chat_id,
            "message": message,
            "access_token": self.app.config.bot.vk_token,
            "keyboard": KeyboardHelper.generate_helping_keyboard(),
            "v": "5.131",
        }
        async with self.session.get(
            _build_query(
                self.API_PATH,
                "messages.send",
                params=params,
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def delete_message(self, chat, message_id):
        pass  # VK API is mostly for tests, no need to clear chat
