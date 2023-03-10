import pytest
import pytest_asyncio

from app.game.models import StatesEnum, Player, Chat
from app.base.dataclasses import UpdateUser, UpdateMessage, Update

update_ids = iter(range(1000))
message_ids = iter(range(1000))


def make_update(author: Player, chat: Chat, text: str) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(id=author.id, username=author.name),
            text=text,
            id=next(message_ids),
            chat_id=chat.id,
        ),
    )


@pytest_asyncio.fixture
def start_game_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/start")


@pytest_asyncio.fixture
def participate_update_player_1(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/participate")


@pytest_asyncio.fixture
def participate_update_player_2(player_2: Player, chat_1: Chat) -> Update:
    return make_update(player_2, chat_1, "/participate")


@pytest_asyncio.fixture
def launch_game_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/launch")


@pytest_asyncio.fixture
def end_game_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/end")


@pytest_asyncio.fixture
def wrong_end_game_update(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/end")


@pytest_asyncio.fixture
def word_update_player_1(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "арк")


@pytest_asyncio.fixture
def word_update_player_2(player_2: Player, chat_1: Chat) -> Update:
    return make_update(player_2, chat_1, "арк")


@pytest_asyncio.fixture
def word_update_creator_1(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "арк")


@pytest_asyncio.fixture
def wrong_word_update_player_1(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "куст")


@pytest_asyncio.fixture
def wrong_word_update_creator_1(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "куст")


@pytest_asyncio.fixture
def creator_vote_yes_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/yes")


@pytest_asyncio.fixture
def creator_vote_no_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/no")


@pytest_asyncio.fixture
def player_vote_yes_update(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/yes")


@pytest_asyncio.fixture
def player_vote_no_update(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/no")
