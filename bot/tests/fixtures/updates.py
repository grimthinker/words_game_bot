import pytest

from app.game_session.models import StatesEnum, Player, Chat
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


@pytest.fixture
def start_game_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/start")


@pytest.fixture
def participate_update_player_1(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/participate")


@pytest.fixture
def participate_update_player_2(player_2: Player, chat_1: Chat) -> Update:
    return make_update(player_2, chat_1, "/participate")


@pytest.fixture
def launch_game_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/launch")


@pytest.fixture
def end_game_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/end")


@pytest.fixture
def wrong_end_game_update(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/end")


@pytest.fixture
def word_update_player_1(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "арк")


@pytest.fixture
def word_update_player_2(player_2: Player, chat_1: Chat) -> Update:
    return make_update(player_2, chat_1, "арк")


@pytest.fixture
def word_update_creator_1(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "арк")


@pytest.fixture
def wrong_word_update_player_1(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "куст")


@pytest.fixture
def wrong_word_update_creator_1(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "куст")


@pytest.fixture
def creator_vote_yes_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/yes")


@pytest.fixture
def creator_vote_no_update(creator_1: Player, chat_1: Chat) -> Update:
    return make_update(creator_1, chat_1, "/no")


@pytest.fixture
def player_vote_yes_update(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/yes")


@pytest.fixture
def player_vote_no_update(player_1: Player, chat_1: Chat) -> Update:
    return make_update(player_1, chat_1, "/no")
