import pytest


@pytest.fixture
async def preparing_state(store, creator_1, start_game_update):
    await store.bots_manager.handle_update(update=start_game_update)
    yield


@pytest.fixture
async def waiting_word_state(
    store, preparing_state, launch_game_update, creator_1, participate_update_player_1
):
    await store.bots_manager.handle_update(update=participate_update_player_1)
    await store.bots_manager.handle_update(update=launch_game_update)
    yield


@pytest.fixture
async def waiting_votes_state(
    store,
    db_session,
    waiting_word_state,
    player_1,
    creator_1,
    word_update_player_1,
    word_update_creator_1,
):
    async with db_session.begin() as session:
        previous_word = await store.game_sessions.get_last_session_word(session, 1)
        prev_player_id = previous_word.proposed_by
        prev_session_player = await store.game_sessions.get_session_player(
            session, prev_player_id, 1
        )
    if prev_session_player.next_player_id == player_1.id:
        await store.bots_manager.handle_update(update=word_update_player_1)
    else:
        await store.bots_manager.handle_update(update=word_update_creator_1)


@pytest.fixture
async def waiting_votes_state_three_players(
    store,
    db_session,
    preparing_state,
    participate_update_player_1,
    participate_update_player_2,
    launch_game_update,
    player_1,
    player_2,
    creator_1,
    word_update_player_1,
    word_update_player_2,
    word_update_creator_1,
):
    await store.bots_manager.handle_update(update=participate_update_player_1)
    await store.bots_manager.handle_update(update=participate_update_player_2)
    await store.bots_manager.handle_update(update=launch_game_update)
    async with db_session.begin() as session:
        previous_word = await store.game_sessions.get_last_session_word(session, 1)
        prev_player_id = previous_word.proposed_by
        prev_session_player = await store.game_sessions.get_session_player(
            session, prev_player_id, 1
        )
    if prev_session_player.next_player_id == player_1.id:
        await store.bots_manager.handle_update(update=word_update_player_1)
    if prev_session_player.next_player_id == creator_1.id:
        await store.bots_manager.handle_update(update=word_update_creator_1)
    else:
        await store.bots_manager.handle_update(update=word_update_player_2)
