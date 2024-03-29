from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
)

from app.store import Store, setup_store
from app.web.config import Config, setup_config
from app.web.logger import setup_logging


class Application(AiohttpApplication):
    store: Optional[Store] = None
    config: Optional[Config] = None


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_store(app)
    return app
