import pytest

from app.store.tg_api.dataclasses import UpdateUser, Update, UpdateMessage

update_ids = iter(range(1000))
message_ids = iter(range(1000))


@pytest.fixture
def start_game_update(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="/start",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def participate_update_player_1(player_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_1.id, is_bot=False, first_name="", username=player_1.name
            ),
            text="/participate",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def participate_update_player_2(player_2, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_2.id, is_bot=False, first_name="", username=player_2.name
            ),
            text="/participate",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def launch_game_update(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="/launch",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def end_game_update(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="/end",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def wrong_end_game_update(player_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_1.id, is_bot=False, first_name="", username=player_1.name
            ),
            text="/end",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def word_update_player_1(player_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_1.id, is_bot=False, first_name="", username=player_1.name
            ),
            text="арк",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def word_update_player_2(player_2, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_2.id, is_bot=False, first_name="", username=player_2.name
            ),
            text="арк",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def word_update_creator_1(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="арк",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def wrong_word_update_player_1(player_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_1.id, is_bot=False, first_name="", username=player_1.name
            ),
            text="куст",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def wrong_word_update_creator_1(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="куст",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def creator_vote_yes_update(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="/yes",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def creator_vote_no_update(creator_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=creator_1.id, is_bot=False, first_name="", username=creator_1.name
            ),
            text="/no",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def player_vote_yes_update(player_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_1.id, is_bot=False, first_name="", username=player_1.name
            ),
            text="/yes",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )


@pytest.fixture
def player_vote_no_update(player_1, chat_1) -> Update:
    return Update(
        id=next(update_ids),
        message=UpdateMessage(
            user=UpdateUser(
                id=player_1.id, is_bot=False, first_name="", username=player_1.name
            ),
            text="/no",
            id=next(message_ids),
            chat_id=chat_1.id,
            date=0,
        ),
    )
