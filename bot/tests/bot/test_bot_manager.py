import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.store import Store
from app.game.models import StatesEnum, Player, Chat
from app.store.tg_api.dataclasses import Update
from app.web.utils import MessageHelper


class TestHandleBaseUpdates:
    @pytest.mark.asyncio
    async def test_handle_start_game(
        self, store: Store, start_game_update: Update, creator_1: Player
    ):
        """Trying start a game session"""
        await store.bots_manager.handle_update(update=start_game_update)
        assert store.external_api.send_message.call_count == 1

    @pytest.mark.asyncio
    async def test_handle_participate(
        self, store: Store, preparing_state, participate_update_player_1
    ):
        """Creates a game session by creator_1, then trying to add player_1 to the game session"""
        await store.bots_manager.handle_update(update=participate_update_player_1)
        assert store.external_api.send_message.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_launch(
        self,
        store: Store,
        participate_update_player_1,
        preparing_state,
        launch_game_update: Update,
    ):
        """Trying to launch a game session"""
        await store.bots_manager.handle_update(update=participate_update_player_1)
        await store.bots_manager.handle_update(update=launch_game_update)
        assert store.external_api.send_message.call_count == 4

    @pytest.mark.asyncio
    async def test_handle_right_word(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        player_1: Player,
        creator_1: Player,
        waiting_word_state,
        word_update_player_1: Update,
        word_update_creator_1: Update,
    ):
        """If one player sends a word that fits the rules, state turns to the vote state."""
        async with db_session.begin() as session:
            previous_word = await store.words.get_last_session_word(
                session, 1, approved=True
            )
            prev_player_id = previous_word.proposed_by
            prev_session_player = await store.players.get_session_player(
                session, prev_player_id, 1
            )
            if prev_session_player.next_player_id == player_1.id:
                await store.bots_manager.handle_update(update=word_update_player_1)
            else:
                await store.bots_manager.handle_update(update=word_update_creator_1)
            assert store.external_api.send_message.call_count == 6

            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )
            assert game_session.state == StatesEnum.VOTE.value

    @pytest.mark.asyncio
    async def test_handle_wrong_word(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        player_1: Player,
        creator_1: Player,
        waiting_word_state,
        wrong_word_update_player_1: Update,
        wrong_word_update_creator_1: Update,
    ):
        """If one player sends a word that doesn't fit the rules, state stays the same."""
        async with db_session.begin() as session:
            previous_word = await store.words.get_last_session_word(
                session, 1, approved=True
            )
            prev_player_id = previous_word.proposed_by
            prev_session_player = await store.players.get_session_player(
                session, prev_player_id, 1
            )
        if prev_session_player.next_player_id == player_1.id:
            await store.bots_manager.handle_update(update=wrong_word_update_player_1)
        else:
            await store.bots_manager.handle_update(update=wrong_word_update_creator_1)
        assert store.external_api.send_message.call_count == 5
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )
        assert game_session.state == StatesEnum.WAITING_WORD.value

    @pytest.mark.asyncio
    async def test_handle_two_full_turns(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        player_1: Player,
        creator_1: Player,
        waiting_word_state,
        word_update_player_1,
        word_update_creator_1,
        player_vote_yes_update: Update,
        creator_vote_yes_update: Update,
        wrong_word_update_player_1: Update,
        wrong_word_update_creator_1: Update,
    ):
        """If one player sends a word that fits the rules, state turns to the vote state."""
        async with db_session.begin() as session:
            previous_word = await store.words.get_last_session_word(
                session, 1, approved=True
            )
            prev_player_id = previous_word.proposed_by
            prev_session_player = await store.players.get_session_player(
                session, prev_player_id, 1
            )

            # first player's turn
        if prev_session_player.next_player_id == player_1.id:
            await store.bots_manager.handle_update(update=word_update_player_1)
        else:
            await store.bots_manager.handle_update(update=word_update_creator_1)

            # players' vote
        if prev_session_player.next_player_id == creator_1.id:
            await store.bots_manager.handle_update(update=player_vote_yes_update)
        else:
            await store.bots_manager.handle_update(update=creator_vote_yes_update)
        assert store.external_api.send_message.call_count == 10

        # second player's turn
        if prev_session_player.next_player_id == player_1.id:
            await store.bots_manager.handle_update(update=wrong_word_update_creator_1)
        else:
            await store.bots_manager.handle_update(update=wrong_word_update_player_1)
        assert store.external_api.send_message.call_count == 12
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )

        # now it should be time for the vote
        assert game_session.state == StatesEnum.VOTE.value

    @pytest.mark.asyncio
    async def test_handle_one_yes_vote(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        player_1: Player,
        creator_1: Player,
        waiting_votes_state,
        creator_vote_yes_update: Update,
        player_vote_yes_update: Update,
    ):
        """Checks the result of one player's vote 'yes'"""
        async with db_session.begin() as session:
            previous_word = await store.words.get_last_session_word(
                session, 1, approved=None
            )
            prev_player_id = previous_word.proposed_by
            prev_session_player = await store.players.get_session_player(
                session, prev_player_id, 1
            )
        if prev_session_player.next_player_id == player_1.id:
            await store.bots_manager.handle_update(update=player_vote_yes_update)
        else:
            await store.bots_manager.handle_update(update=creator_vote_yes_update)
        assert store.external_api.send_message.call_count == 10
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )
        assert game_session.state == StatesEnum.WAITING_WORD.value

    @pytest.mark.asyncio
    async def test_handle_one_no_vote(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        player_1: Player,
        creator_1: Player,
        waiting_votes_state,
        player_vote_no_update: Update,
        creator_vote_no_update: Update,
    ):
        """Checks the result of the one player's vote 'no'. In two players session
        that means the second player's lost and the end of the session"""
        async with db_session.begin() as session:
            previous_word = await store.words.get_last_session_word(
                session, 1, approved=None
            )
            prev_player_id = previous_word.proposed_by
            prev_session_player = await store.players.get_session_player(
                session, prev_player_id, 1
            )
        if prev_session_player.next_player_id == player_1.id:
            await store.bots_manager.handle_update(update=player_vote_no_update)
        else:
            await store.bots_manager.handle_update(update=creator_vote_no_update)
        assert store.external_api.send_message.call_count == 11
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id, StatesEnum.ENDED.value
            )
        assert game_session

    @pytest.mark.asyncio
    async def test_handle_repeating_yes_vote(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        player_1: Player,
        player_2: Player,
        creator_1: Player,
        waiting_votes_state_three_players,
        creator_vote_yes_update: Update,
        player_vote_yes_update: Update,
    ):
        """Checks the result of one player's repeating vote 'yes'. The session should stay in the waiting_vote
        state after that"""
        async with db_session.begin() as session:
            previous_word = await store.words.get_last_session_word(
                session, 1, approved=None
            )
            prev_player_id = previous_word.proposed_by
            prev_session_player = await store.players.get_session_player(
                session, prev_player_id, 1
            )
        if prev_session_player.next_player_id == player_1.id:
            for _ in range(3):
                await store.bots_manager.handle_update(update=player_vote_yes_update)
        else:
            for _ in range(3):
                await store.bots_manager.handle_update(update=creator_vote_yes_update)
        assert store.external_api.send_message.call_count == 10
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )
        assert game_session.state == StatesEnum.VOTE.value

    @pytest.mark.asyncio
    async def test_word_timeout(
        self,
        db_session: AsyncSession,
        server,
        chat_1: Chat,
        store: Store,
        waiting_word_state,
    ):
        """Checks the work of the word-waiting timer. When the timer works, one player loses, in two players session
        that means the second player's victory and the end of the session"""
        await asyncio.sleep(server.config.game.word_wait_time + 0.2)
        assert store.external_api.send_message.call_count == 7
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id, StatesEnum.ENDED.value
            )
            players_in_session = await store.players.get_session_players(session, 1)
        assert game_session
        is_dropped_out = False
        for session_player in players_in_session:
            if session_player.is_dropped_out:
                is_dropped_out = True
        assert is_dropped_out

    @pytest.mark.asyncio
    async def test_vote_timeout(
        self,
        db_session: AsyncSession,
        server,
        chat_1: Chat,
        store: Store,
        waiting_votes_state,
    ):
        """Checks the work of the vote-waiting timer. When the timer works, starts result summarizing."""
        await asyncio.sleep(server.config.game.vote_wait_time + 0.2)
        assert store.external_api.send_message.call_count == 9
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )
        assert game_session.state == StatesEnum.WAITING_WORD.value

    @pytest.mark.asyncio
    async def test_handle_end_update_from_word_wait(
        self,
        db_session,
        server,
        chat_1,
        store: Store,
        waiting_word_state,
        end_game_update: Update,
    ):
        """Checks handling /end update from the creator from waiting_word_state"""
        await store.bots_manager.handle_update(update=end_game_update)
        assert store.external_api.send_message.call_count == 5
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id, StatesEnum.ENDED.value
            )
        assert game_session

    @pytest.mark.asyncio
    async def test_handle_end_update_from_voting(
        self,
        db_session: AsyncSession,
        server,
        chat_1: Chat,
        store: Store,
        waiting_votes_state_three_players,
        end_game_update: Update,
    ):
        """Checks handling /end update from the creator from waiting_votes_state"""
        await store.bots_manager.handle_update(update=end_game_update)
        assert store.external_api.send_message.call_count == 8
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id, StatesEnum.ENDED.value
            )
        assert game_session

    @pytest.mark.asyncio
    async def test_handle_end_update_from_preparing(
        self,
        db_session: AsyncSession,
        server,
        chat_1,
        store: Store,
        preparing_state,
        end_game_update: Update,
    ):
        """Checks handling /end update from the creator while session in preparing_state"""
        await store.bots_manager.handle_update(update=end_game_update)
        assert store.external_api.send_message.call_count == 2
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id, StatesEnum.ENDED.value
            )
        assert game_session


class TestHandleWrongUpdates:
    async def test_handle_participate_no_session(
        self,
        store: Store,
        participate_update_player_1: Update,
    ):
        await store.bots_manager.handle_update(update=participate_update_player_1)
        assert store.external_api.send_message.call_count == 1
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.no_session

    async def test_handle_launch_no_session(
        self,
        store: Store,
        launch_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=launch_game_update)
        assert store.external_api.send_message.call_count == 1
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.no_session

    async def test_handle_vote_no_session(
        self,
        store: Store,
        player_vote_yes_update: Update,
    ):
        await store.bots_manager.handle_update(update=player_vote_yes_update)
        assert store.external_api.send_message.call_count == 1
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.no_session

    async def test_handle_launch_one_player(
        self,
        store: Store,
        preparing_state,
        launch_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=launch_game_update)
        assert store.external_api.send_message.call_count == 2
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.too_few_players

    async def test_handle_participate_launched_session(
        self,
        store: Store,
        waiting_word_state,
        participate_update_player_2: Update,
    ):
        await store.bots_manager.handle_update(update=participate_update_player_2)
        assert store.external_api.send_message.call_count == 5
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.cant_join_now

    async def test_handle_participate_while_voting(
        self,
        store: Store,
        db_session: AsyncSession,
        waiting_votes_state,
        participate_update_player_2: Update,
    ):
        await store.bots_manager.handle_update(update=participate_update_player_2)
        assert store.external_api.send_message.call_count == 7
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.cant_join_now

    async def test_handle_start_while_preparing(
        self,
        store: Store,
        preparing_state,
        start_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=start_game_update)
        assert store.external_api.send_message.call_count == 2
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.already_started

    async def test_handle_start_while_wait_word(
        self,
        store: Store,
        waiting_word_state,
        start_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=start_game_update)
        assert store.external_api.send_message.call_count == 5
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.already_started

    async def test_handle_start_while_vote(
        self,
        store: Store,
        waiting_votes_state,
        start_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=start_game_update)
        assert store.external_api.send_message.call_count == 7
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.already_started

    async def test_handle_launch_while_wait_word(
        self,
        store: Store,
        waiting_word_state,
        launch_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=launch_game_update)
        assert store.external_api.send_message.call_count == 5
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.already_launched

    async def test_handle_launch_while_vote(
        self,
        store: Store,
        waiting_votes_state,
        launch_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=launch_game_update)
        assert store.external_api.send_message.call_count == 7
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.already_launched

    async def test_handle_vote_while_preparing(
        self,
        store: Store,
        preparing_state,
        player_vote_yes_update: Update,
    ):
        await store.bots_manager.handle_update(update=player_vote_yes_update)
        assert store.external_api.send_message.call_count == 2
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.game_is_not_launched

    async def test_handle_vote_while_waiting_word(
        self,
        store: Store,
        db_session: AsyncSession,
        waiting_word_state,
        chat_1: Chat,
        player_vote_yes_update: Update,
    ):
        await store.bots_manager.handle_update(update=player_vote_yes_update)
        assert store.external_api.send_message.call_count == 5
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.no_word_to_vote
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id
            )
        assert game_session.state == StatesEnum.WAITING_WORD.value

    async def test_handle_word_while_preparing(
        self,
        store: Store,
        preparing_state,
        word_update_creator_1: Update,
    ):
        assert store.external_api.send_message.call_count == 1
        await store.bots_manager.handle_update(update=word_update_creator_1)
        assert store.external_api.send_message.call_count == 1

    async def test_handle_word_while_vote(
        self,
        store: Store,
        waiting_votes_state,
        word_update_creator_1: Update,
    ):
        assert store.external_api.send_message.call_count == 6
        await store.bots_manager.handle_update(update=word_update_creator_1)
        assert store.external_api.send_message.call_count == 6

    async def test_handle_end_after_end(
        self,
        store: Store,
        preparing_state,
        end_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=end_game_update)
        await store.bots_manager.handle_update(update=end_game_update)
        assert store.external_api.send_message.call_count == 3
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.no_session

    async def test_handle_end_not_creator(
        self,
        store: Store,
        db_session: AsyncSession,
        chat_1: Chat,
        waiting_votes_state,
        wrong_end_game_update: Update,
    ):
        await store.bots_manager.handle_update(update=wrong_end_game_update)
        assert store.external_api.send_message.call_count == 7
        assert store.external_api.send_message.mock_calls[-1].kwargs["message"] == MessageHelper.cant_end
        async with db_session.begin() as session:
            game_session = await store.game_sessions.get_current_session(
                session, chat_1.id, StatesEnum.PREPARING.value
            )
        assert game_session