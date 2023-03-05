import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_session.models import (
    GameSessionModel,
    GameSession,
    ChatModel,
    Chat,
    PlayerModel,
    Player,
)


@pytest.fixture
async def player_1(db_session: AsyncSession) -> Player:
    name = "Шанкрес"
    player = PlayerModel(name=name, id=101)
    async with db_session.begin() as session:
        session.add(player)
    return Player(id=player.id, name=player.name)


@pytest.fixture
async def player_2(db_session: AsyncSession) -> Player:
    name = "Викей"
    player = PlayerModel(name=name, id=102)
    async with db_session.begin() as session:
        session.add(player)
    return Player(id=player.id, name=player.name)


@pytest.fixture
async def player_3(db_session: AsyncSession) -> Player:
    name = "Юниус"
    player = PlayerModel(name=name, id=103)
    async with db_session.begin() as session:
        session.add(player)
    return Player(id=player.id, name=player.name)


@pytest.fixture
async def creator_1(db_session: AsyncSession) -> Player:
    name = "Тринетт"
    player = PlayerModel(name=name, id=11)
    async with db_session.begin() as session:
        session.add(player)
    return Player(id=player.id, name=player.name)


@pytest.fixture
async def creator_2(db_session: AsyncSession) -> Player:
    name = "Иша"
    player = PlayerModel(name=name, id=12)
    async with db_session.begin() as session:
        session.add(player)
    return Player(id=player.id, name=player.name)


@pytest.fixture
async def chat_1(db_session: AsyncSession) -> Chat:
    chat = ChatModel(id=1000)
    async with db_session.begin() as session:
        session.add(chat)
    return Chat(id=chat.id)


@pytest.fixture
async def chat_2(db_session: AsyncSession) -> Chat:
    chat = ChatModel(id=2000)
    async with db_session.begin() as session:
        session.add(chat)
    return Chat(id=chat.id)


@pytest.fixture
async def game_session_1(
    db_session: AsyncSession, chat_1: Chat, creator_1: Player
) -> GameSession:
    game_session = GameSessionModel(
        chat_id=chat_1.id,
        creator_id=creator_1.id,
        state=0,
    )
    async with db_session.begin() as session:
        session.add(game_session)
    return GameSessionModel.to_dc(game_session, creator_1, [creator_1])


@pytest.fixture
async def game_session_2(
    db_session: AsyncSession, chat_2: Chat, creator_2: Player
) -> GameSession:
    game_session = GameSessionModel(
        chat_id=chat_2.id,
        creator_id=creator_2.id,
        state=0,
    )
    async with db_session.begin() as session:
        session.add(game_session)
    return GameSessionModel.to_dc(game_session, creator_2, [creator_2])
