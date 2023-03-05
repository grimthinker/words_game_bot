import typing

from app.store.database.database import Database
from app.store.bot.constants import API

if typing.TYPE_CHECKING:
    from poller.app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.rabbitmq.accessor import RabbitAccessor
        from app.store.tg_api.accessor import TGApiAccessor
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.bot.manager import BotManager
        from app.store.game_session.accessor import GameSessionAccessor

        self.game_sessions = GameSessionAccessor(app)
        if API == "tg":
            self.external_api = TGApiAccessor(app)
        else:
            self.external_api = VkApiAccessor(app)
        self.rabbit_accessor = RabbitAccessor(app)
        self.bots_manager = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
    app.on_startup.append(app.store.bots_manager.on_bot_initializing)
