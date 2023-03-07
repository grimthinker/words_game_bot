import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from poller.app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.rabbitmq.accessor import RabbitAccessor
        from app.store.tg_api.accessor import TGApiAccessor
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.bot.manager import BotManager
        from app.store.game_session.accessor import GameSessionAccessor
        from app.store.chat.accessor import ChatAccessor
        from app.store.player.accessor import PlayerAccessor
        from app.store.vote.accessor import VoteAccessor
        from app.store.word.accessor import WordAccessor

        self.game_sessions = GameSessionAccessor(app)
        self.chats = ChatAccessor(app)
        self.players = PlayerAccessor(app)
        self.votes = VoteAccessor(app)
        self.words = WordAccessor(app)
        if app.config.bot.api == "tg":
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
