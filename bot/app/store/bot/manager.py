import typing
from logging import getLogger
from typing import Union, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.game_session.models import GameSession, StatesEnum, Player, Word, SessionPlayer
from app.store.bot.constants import BOT_ID, BOT_NAME, BASIC_COMMANDS, WORD_ENTER_TIME, VOTE_TIME
from app.store.bot.helpers import AsyncTimer, generate_some_order, check_word, list_results, MessageHelper, \
    remove_timer
from app.store.tg_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")
        self.word_timers = dict()
        self.vote_timers = dict()


    async def on_bot_initializing(self, app: "Application"):
        async with self.app.database.session.begin() as db_session:
            sessions = await self.app.store.game_sessions.get_sessions(db_session, state_not=StatesEnum.ENDED.value)
            for session in sessions:
                if session.state == StatesEnum.WAITING_WORD.value:
                    word = await self.app.store.game_sessions.get_last_session_word(db_session, session.id, approved=True)
                    next_player = await self.app.store.game_sessions.get_next_player(db_session, word.proposed_by, session.id)
                    await self.wait_word(session, next_player, word)
                if session.state == StatesEnum.VOTE.value:
                    word = await self.app.store.game_sessions.get_last_session_word(db_session, session.id)
                    await self.wait_vote(session, word)


    async def handle_update(self, update: Update) -> None:
        async with self.app.database.session.begin() as db_session:
            await self.confirm_chat_in_db(db_session, update)
            await self.confirm_user_in_db(db_session, update)
            session = await self.app.store.game_sessions.get_current_session(db_session, update.message.chat_id)
            update = await self.delete_if_wrong_message(update, session)
            if not update:
                return
            elif update.message.text == "/start":
                await self.on_start(db_session, update, session)
            elif update.message.text == "/participate":
                await self.on_participate(db_session, update, session)
            elif update.message.text == "/launch":
                await self.on_launch_game(db_session, update, session)
            elif update.message.text in ["/yes", "/no"]:
                await self.on_vote(db_session, update, session)
            elif update.message.text == "/end":
                await self.on_end_session(db_session, update, session)
            else:
                await self.on_word_entered(db_session, update, session)


    async def on_start(self, db_session: AsyncSession, update: Update, session: GameSession = None):
        if session:
            await self.send_message(update.message.chat_id, MessageHelper.already_started)
            return
        await self.app.store.game_sessions.create_session(db_session,
                                                          update.message.chat_id,
                                                          update.message.user.id)
        await self.send_message(update.message.chat_id, MessageHelper.started(update))


    async def on_participate(self, db_session: AsyncSession, update: Update, session: GameSession = None):
        """ Adding a new player to game_session, after some checks """
        if not session or session.state == StatesEnum.ENDED.value:
            await self.send_message(update.message.chat_id, MessageHelper.no_session)
            return
        if session.state != StatesEnum.PREPARING.value:
            await self.send_message(update.message.chat_id, MessageHelper.cant_join_now)
            return
        session_player = await self.app.store.game_sessions.get_session_player(db_session,
                                                                                     update.message.user.id,
                                                                                     session.id)
        if session_player:
            await self.send_message(update.message.chat_id, MessageHelper.already_participates(update))
            return
        await self.app.store.game_sessions.add_player_to_session(db_session,
                                                                 update.message.user.id,
                                                                 session.id)
        await self.send_message(update.message.chat_id, MessageHelper.joined(update))


    async def on_launch_game(self, db_session: AsyncSession, update: Update, session: GameSession = None):
        if not session or session.state == StatesEnum.ENDED.value:
            await self.send_message(update.message.chat_id, MessageHelper.no_session)
            return
        if session.state != StatesEnum.PREPARING.value:
            await self.send_message(update.message.chat_id, MessageHelper.already_launched)
            return
        if session.creator.id != update.message.user.id:
            await self.send_message(update.message.chat_id, MessageHelper.not_creator_to_launch(update))
            return
        if len(session.players) < 2:
            await self.send_message(update.message.chat_id, MessageHelper.too_dew_players)
            return
        await self.send_message(update.message.chat_id, MessageHelper.launched)
        await self.launch_session(db_session, session)


    async def on_word_entered(self, db_session: AsyncSession, update: Update, session: GameSession = None) -> None:
        """ Verifying that everything ok then stopping the corresponding wait-word-timer and calling self.start_vote """
        if not session or session.state == StatesEnum.ENDED.value:
            await self.send_message(update.message.chat_id, MessageHelper.no_session)
            return
        session_player = await self.app.store.game_sessions.get_session_player(db_session,
                                                                                     update.message.user.id,
                                                                                     session.id)
        previous_word = await self.app.store.game_sessions.get_last_session_word(db_session,
                                                                                 session.id,
                                                                                 approved=True)
        proposed_word = update.message.text
        prev_player_id = previous_word.proposed_by
        req_answerer = await self.app.store.game_sessions.get_next_player(db_session, prev_player_id, session.id)
        if not session_player.player_id == req_answerer.id:
            await self.send_message(update.message.chat_id, MessageHelper.wrong_player_turn(update))
            return
        if not check_word(proposed_word, previous_word.word):
            await self.send_message(update.message.chat_id, MessageHelper.word_doesnt_fit(update))
            return

        await self.send_message(update.message.chat_id, MessageHelper.word_proposed(update))
        word = await self.app.store.game_sessions.add_session_word(db_session,
                                                                    update.message.user.id,
                                                                    previous_word.id,
                                                                    proposed_word,
                                                                    session.id)
        await self.start_vote(db_session, session, word)
        await db_session.commit()
        remove_timer(self.word_timers, session.id)


    async def on_vote(self, db_session: AsyncSession, update: Update, session: GameSession) -> None:
        """ Verifying that everything ok then calling self.vote """
        if not session or session.state == StatesEnum.ENDED.value:
            await self.send_message(update.message.chat_id, MessageHelper.no_session)
            return
        if session.state == StatesEnum.PREPARING.value:
            await self.send_message(update.message.chat_id, MessageHelper.game_is_not_launched)
            return
        if session.state == StatesEnum.WAITING_WORD.value:
            await self.send_message(update.message.chat_id, MessageHelper.no_word_to_vote)
            return
        word_to_vote = await self.app.store.game_sessions.get_last_session_word(db_session,
                                                                                 session.id)
        existing_vote = await self.app.store.game_sessions.has_voted(db_session, update.message.user.id, word_to_vote.id)
        if existing_vote:
            await self.send_message(update.message.chat_id, MessageHelper.already_voted(update))
            return
        session_players = await self.check_vote_allowance(db_session, update, word_to_vote, session)
        if not session_players:
            await self.send_message(update.message.chat_id, MessageHelper.cant_vote(update))
            return

        # Very likely we don't need to check this, but I'm only 98% sure
        if word_to_vote.approved:
            return
        await self.vote(db_session, update, word_to_vote, session, session_players)


    async def on_end_session(self, db_session: AsyncSession, update: Update, session: GameSession):
        if session.creator.id == update.message.user.id:
            remove_timer(self.word_timers, session.id)
            remove_timer(self.vote_timers, session.id)
            await self.app.store.game_sessions.set_session_state(db_session, session.id, StatesEnum.ENDED.value)
            session_players = await self.app.store.game_sessions.get_session_players(db_session, session.id)
            await self.send_message(update.message.chat_id, MessageHelper.game_results(session_players))
        else:
            self.app.store.external_api.delete_message(update.message.chat_id, update.message.id)


    async def send_message(self, chat_id: int, message: str) -> None:
        params = {"chat_id": chat_id, "message": message}
        await self.app.store.external_api.send_message(**params)


    async def confirm_chat_in_db(self, db_session: AsyncSession, update: Update) -> None:
        chat = await self.app.store.game_sessions.get_chat(db_session, update.message.chat_id)
        if not chat:
            await self.app.store.game_sessions.add_chat_to_db(db_session, update.message.chat_id)


    async def confirm_user_in_db(self, db_session: AsyncSession, update: Update) -> None:
        user = await self.app.store.game_sessions.get_player_by_id(db_session, update.message.user.id)
        if not user:
            await self.app.store.game_sessions.add_player_to_db(db_session,
                                                                update.message.user.id,
                                                                update.message.user.username)


    async def launch_session(self, db_session: AsyncSession, session: GameSession) -> Word:
        players = session.players
        required_order = list(generate_some_order(players))
        await self.app.store.game_sessions.assign_players_order(db_session, session.id, required_order)
        first_word = await self.app.store.game_sessions.set_first_word(db_session, session.id)
        first_player = await self.app.store.game_sessions.choose_first_player(db_session, players, session.id)
        await self.app.store.game_sessions.set_session_state(db_session, session.id, StatesEnum.WAITING_WORD.value)
        await self.wait_word(session, first_player, first_word)
        return first_word


    async def start_vote(self, db_session: AsyncSession, session: GameSession, word: Word) -> None:
        """ Setting the VOTE state of the game session and starting the wait votes timer """
        await self.app.store.game_sessions.set_session_state(db_session, session.id, StatesEnum.VOTE.value)
        await self.wait_vote(session, word)


    async def wait_word(self, session: GameSession, player: Player, last_word: Word) -> None:
        await self.send_message(session.chat_id, MessageHelper.remind_word_for_next(last_word, player))
        timer = AsyncTimer(timeout=self.app.config.game.word_wait_time,
                           callback=self.drop_player,
                           callback_params={"session": session, "player": player, "last_word": last_word, "from_timer": True},
                           app=self.app)
        self.word_timers[session.id] = timer


    async def wait_vote(self, session: GameSession, word: Word) -> None:
        await self.send_message(session.chat_id, MessageHelper.vote_for_word(word))
        timer = AsyncTimer(timeout=self.app.config.game.vote_wait_time,
                           callback=self.check_vote_results,
                           callback_params={"session": session, "from_timer": True},
                           app=self.app)
        self.vote_timers[session.id] = timer


    async def drop_player(self, db_session: AsyncSession, session: GameSession, player: Player, last_word: Word, from_timer: bool=None) -> None:
        await self.app.store.game_sessions.drop_player(db_session, player.id, session.id)
        if from_timer:
            await self.send_message(session.chat_id, MessageHelper.time_for_word_ended)

        # If only one real player is left (plus bot who has proposed the first word), then we need to end this
        # game session. So let's verify this
        session_players = await self.app.store.game_sessions.get_session_players(db_session, session.id)
        remaining_players = [player for player in session_players if not player.is_dropped_out and player.player_id != BOT_ID]
        if len(remaining_players) < 2:
            remaining_player = await self.app.store.game_sessions.get_player_by_id(db_session, remaining_players[0].player_id)
            await self.app.store.game_sessions.set_session_state(db_session, session.id, StatesEnum.ENDED.value)
            await self.send_message(session.chat_id, MessageHelper.announce_winner(remaining_player))
            await self.send_message(session.chat_id, MessageHelper.game_results(session_players))
            return

        # If there are more than one player left, set wait-for-word timer for the next one player. Game session state
        # remains as WAITING_WORD
        next_player = await self.app.store.game_sessions.get_next_player(db_session, player.id, session.id)
        await db_session.commit()
        await self.wait_word(session, next_player, last_word)


    async def check_vote_results(self, db_session: AsyncSession, session: GameSession, word_votes: list[bool]=None, from_timer: bool=None) -> None:
        if from_timer:
            await self.send_message(session.chat_id, MessageHelper.time_for_vote_ended)
        else:
            await self.send_message(session.chat_id, MessageHelper.all_players_voted)
        word_to_vote = await self.app.store.game_sessions.get_last_session_word(db_session,
                                                                                session.id)
        if not word_votes:
            word_votes = await self.app.store.game_sessions.get_word_votes(db_session, word_to_vote.id)

        yes_votes = [vote for vote in word_votes if vote]
        player = await self.app.store.game_sessions.get_player_by_id(db_session, word_to_vote.proposed_by)
        next_player = await self.app.store.game_sessions.get_next_player(db_session, player.id, session.id)
        if len(word_votes) == 0 or len(yes_votes) / len(word_votes) >= 0.5:
            await self.app.store.game_sessions.set_vote_result(db_session, word_to_vote.id, True)
            points = await self.app.store.game_sessions.accrue_points(db_session, word_to_vote.proposed_by, session.id, word_to_vote.word)
            await self.app.store.game_sessions.set_session_state(db_session, session.id, StatesEnum.WAITING_WORD.value)
            await self.send_message(session.chat_id, MessageHelper.vote_result_positive(word_to_vote, player, points))
            await self.wait_word(session, next_player, word_to_vote)
        else:
            await self.app.store.game_sessions.set_vote_result(db_session, word_to_vote.id, False)
            await self.drop_player(db_session, session, next_player, word_to_vote)
            await self.send_message(session.chat_id, MessageHelper.vote_result_negative(word_to_vote, player))


    async def check_vote_allowance(self, db_session: AsyncSession, update: Update, word_to_vote: Word, session: GameSession) -> Optional[list[SessionPlayer]]:
        """
        To be able to vote for a word the player has to participate in the game session, not to be
        dropped, and not to be the one proposing the word. So here we are, checking this...
        """
        player_id = update.message.user.id
        session_players = await self.app.store.game_sessions.get_session_players(db_session, session.id)
        filtered = list(filter(lambda player: player.player_id == player_id, session_players))
        session_player = filtered[0] if filtered else None
        if not session_player or session_player.is_dropped_out or session_player.player_id == word_to_vote.proposed_by:
            return None
        # We will need to check if all the players have voted right after when this one has voted,
        # so return players list here lest make the same one select from db later
        return session_players


    async def vote(self, db_session: AsyncSession, update: Update, word_to_vote: Word, session: GameSession, session_players: list[SessionPlayer]):
        """ Make the record in db about the vote from player and, if all players have voted, cancel wait-vote timer """
        await self.app.store.game_sessions.vote(db_session, update.message.user.id, update.message.text, word_to_vote.id)
        await self.send_message(session.chat_id, MessageHelper.on_someones_vote(update, word_to_vote))
        all_voted = await self.check_if_all_voted(db_session, word_to_vote, session_players)
        if all_voted:
            # If true, we don't need to wait anymore and may cancel the corresponding vote timer
            remove_timer(self.vote_timers, session.id)
            await self.check_vote_results(db_session, session, all_voted)


    async def check_if_all_voted(self, db_session: AsyncSession, session_word: Word, session_players: list[SessionPlayer]) -> Optional[list[bool]]:
        """ Verifying everyone remaining (excluding bot) has voted """
        word_votes = await self.app.store.game_sessions.get_word_votes(db_session, session_word.id)
        remaining_players = [player for player in session_players if not player.is_dropped_out and player.player_id != BOT_ID]
        if len(word_votes) == len(remaining_players) - 1:
            return [vote for vote in word_votes]

    async def delete_if_wrong_message(self, update: Update, session: GameSession = None) -> Optional[Update]:
        """ Clearing chat from some littering messages on every update, if the external_api allows to delete them """
        text = update.message.text
        separate_words = text.split()
        first = separate_words[0]
        appropriate_state = False
        if session and session.state == StatesEnum.WAITING_WORD.value:
            appropriate_state = True
        if len(separate_words) == 1:
            if first in BASIC_COMMANDS or appropriate_state:
                return update
        await self.app.store.external_api.delete_message(update.message.chat_id, update.message.id)
