from sqlalchemy import text

import logging
from typing import Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database.sqlalchemy_base import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[sessionmaker] = None

    def _build_async_db_uri(self):
        user = self.app.config.database.user
        password = self.app.config.database.password
        db_name = self.app.config.database.database
        host = self.app.config.database.host
        port = self.app.config.database.port
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(
            self._build_async_db_uri(), echo=True, future=True
        )
        self.session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )
        await self.clear_db()  # Remove this when all is done

    async def disconnect(self, *_: list, **__: dict) -> None:
        await self.clear_db()
        try:
            await self._engine.dispose()
        except Exception as err:
            logging.warning(err)

    async def clear_db(self):
        async with self.app.database.session() as session:
            tables = (
                "players",
                "chats",
                "admins",
                "association_players_sessions",
                "game_sessions",
                "session_words",
                "votes",
                "game_rules",
                "time_settings",
            )
            for table in tables:
                await session.execute(text(f"TRUNCATE {table} CASCADE"))
                await session.commit()
            for table in ["game_sessions", "admins", "session_words"]:
                await session.execute(
                    text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1")
                )
                await session.commit()
