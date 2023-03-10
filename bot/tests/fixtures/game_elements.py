import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.game.models import (
    GameSessionModel,
    GameSession,
    ChatModel,
    Chat,
    PlayerModel,
    Player,
)


@pytest_asyncio.fixture
async def player_1(db_session: AsyncSession) -> Player:
    name = "Шанкрес"
    player = PlayerModel(name=name, id=101)
    async with db_session.begin() as session:
        session.add(player)
    yield Player(id=player.id, name=player.name)


@pytest_asyncio.fixture
async def player_2(db_session: AsyncSession) -> Player:
    name = "Викей"
    player = PlayerModel(name=name, id=102)
    async with db_session.begin() as session:
        session.add(player)
    yield Player(id=player.id, name=player.name)


@pytest_asyncio.fixture
async def player_3(db_session: AsyncSession) -> Player:
    name = "Юниус"
    player = PlayerModel(name=name, id=103)
    async with db_session.begin() as session:
        session.add(player)
    yield Player(id=player.id, name=player.name)


@pytest_asyncio.fixture
async def creator_1(db_session: AsyncSession) -> Player:
    name = "Тринетт"
    player = PlayerModel(name=name, id=11)
    async with db_session.begin() as session:
        session.add(player)
    yield Player(id=player.id, name=player.name)


@pytest_asyncio.fixture
async def creator_2(db_session: AsyncSession) -> Player:
    name = "Иша"
    player = PlayerModel(name=name, id=12)
    async with db_session.begin() as session:
        session.add(player)
    yield Player(id=player.id, name=player.name)


@pytest_asyncio.fixture
async def chat_1(db_session: AsyncSession) -> Chat:
    chat = ChatModel(id=1000)
    async with db_session.begin() as session:
        session.add(chat)
    return Chat(id=chat.id)


@pytest_asyncio.fixture
async def chat_2(db_session: AsyncSession) -> Chat:
    chat = ChatModel(id=2000)
    async with db_session.begin() as session:
        session.add(chat)
    return Chat(id=chat.id)
