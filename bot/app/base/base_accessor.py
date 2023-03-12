import typing
from logging import getLogger
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")
        self.session: Optional[ClientSession] = None
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
