import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.store import Store
from app.game_session.models import StatesEnum, Player, Chat
from app.store.tg_api.dataclasses import Update


@pytest.fixture
async def preparing_state(store: Store, creator_1: Player, start_game_update: Update):
    await store.bots_manager.handle_update(update=start_game_update)
    yield


@pytest.fixture
async def waiting_word_state(
    store: Store,
    preparing_state,
    launch_game_update: Update,
    creator_1: Player,
    participate_update_player_1: Update,
):
    await store.bots_manager.handle_update(update=participate_update_player_1)
    await store.bots_manager.handle_update(update=launch_game_update)
    yield


@pytest.fixture
async def waiting_votes_state(
    store: Store,
    db_session: AsyncSession,
    waiting_word_state,
    player_1: Player,
    creator_1: Player,
    word_update_player_1: Update,
    word_update_creator_1: Update,
):
    async with db_session.begin() as session:
        previous_word = await store.words.get_last_session_word(session, 1)
        prev_player_id = previous_word.proposed_by
        prev_session_player = await store.players.get_session_player(
            session, prev_player_id, 1
        )
    if prev_session_player.next_player_id == player_1.id:
        await store.bots_manager.handle_update(update=word_update_player_1)
    else:
        await store.bots_manager.handle_update(update=word_update_creator_1)


@pytest.fixture
async def waiting_votes_state_three_players(
    store: Store,
    db_session: AsyncSession,
    player_1: Player,
    player_2: Player,
    creator_1: Player,
    preparing_state,
    participate_update_player_1: Update,
    participate_update_player_2: Update,
    launch_game_update: Update,
    word_update_player_1: Update,
    word_update_player_2: Update,
    word_update_creator_1: Update,
):
    await store.bots_manager.handle_update(update=participate_update_player_1)
    await store.bots_manager.handle_update(update=participate_update_player_2)
    await store.bots_manager.handle_update(update=launch_game_update)
    async with db_session.begin() as session:
        previous_word = await store.words.get_last_session_word(session, 1)
        prev_player_id = previous_word.proposed_by
        prev_session_player = await store.players.get_session_player(
            session, prev_player_id, 1
        )
    if prev_session_player.next_player_id == player_1.id:
        await store.bots_manager.handle_update(update=word_update_player_1)
    if prev_session_player.next_player_id == creator_1.id:
        await store.bots_manager.handle_update(update=word_update_creator_1)
    else:
        await store.bots_manager.handle_update(update=word_update_player_2)
