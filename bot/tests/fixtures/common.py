import logging
import os
from hashlib import sha256
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiohttp.test_utils import TestClient, loop_context
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import Admin, AdminModel
from app.game.models import PlayerModel, Player
from app.store import Database
from app.store import Store
from app.store.bot.constants import BOT_ID, BOT_NAME
from app.web.app import setup_app
from app.web.config import Config

from app.store.bot.helpers import remove_timer


@pytest_asyncio.fixture(scope="session")
def event_loop():
    with loop_context() as _loop:
        yield _loop


@pytest_asyncio.fixture(scope="session")
async def server():
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.store.rabbit_accessor = AsyncMock()
    app.store.external_api = AsyncMock()
    app.store.external_api.send_message = AsyncMock()
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)
    return app


@pytest_asyncio.fixture(autouse=True)
def reset_send_message_mock(store):
    yield
    store.external_api.send_message.reset_mock()


@pytest_asyncio.fixture
async def store(server) -> Store:
    return server.store


@pytest_asyncio.fixture
async def db_session(server):
    return server.database.session


@pytest_asyncio.fixture(autouse=True, scope="function")
async def clear_db(server):
    yield
    remove_timer(server.store.bots_manager.word_timers, 1)
    remove_timer(server.store.bots_manager.vote_timers, 1)
    try:
        session = AsyncSession(server.database._engine)
        connection = await session.connection()
        for table in server.database._db.metadata.tables:
            await session.execute(text(f"TRUNCATE {table} CASCADE"))
            await session.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1"))

        await session.commit()
        connection.close()

    except Exception as err:
        logging.warning(err)


@pytest_asyncio.fixture
def config(server) -> Config:
    return server.config


@pytest_asyncio.fixture(autouse=True)
def cli(aiohttp_client, event_loop, server) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(server))


@pytest_asyncio.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin.login",
        data={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    return cli


@pytest_asyncio.fixture(autouse=True)
async def admin(cli, db_session, config: Config) -> Admin:
    new_admin = AdminModel(
        email=config.admin.email,
        password=sha256(config.admin.password.encode()).hexdigest(),
    )
    async with db_session.begin() as session:
        session.add(new_admin)

    return Admin(id=new_admin.id, email=new_admin.email)


@pytest_asyncio.fixture(autouse=True)
async def bot(cli, db_session, config: Config) -> Player:
    bot = PlayerModel(id=BOT_ID, name=BOT_NAME)
    async with db_session.begin() as session:
        session.add(bot)
    return Player(id=bot.id, name=bot.name)
