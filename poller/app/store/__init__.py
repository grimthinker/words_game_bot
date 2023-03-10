import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.rabbitmq.accessor import RabbitAccessor
        from app.store.tg_api.accessor import TGApiAccessor
        from app.store.vk_api.accessor import VkApiAccessor

        if app.config.bot.api == "tg":
            self.external_api = TGApiAccessor(app)
        else:
            self.external_api = VkApiAccessor(app)
        self.rabbit_accessor = RabbitAccessor(app)


def setup_store(app: "Application"):
    app.store = Store(app)
