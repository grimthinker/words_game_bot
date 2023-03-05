import random
from typing import Optional, Union, Iterator, Iterable, List
from sqlalchemy import select, or_, and_, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game_session.models import ChatModel, Chat, PlayerModel, Player, GameSessionModel, GameSession, StatesEnum, \
    PlayersSessions, SessionPlayer, SessionWords, Word, WordVotes
from app.store.bot.constants import BOT_ID, BOT_NAME, START_WORDS, TEST_WORD
from app.store.bot.helpers import judge_word


class GameSessionAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        async with self.app.database.session() as db_session:
            await self.app.store.game_sessions.add_player_to_db(db_session, BOT_ID, BOT_NAME)
            await db_session.commit()


    async def add_chat_to_db(self, db_session: AsyncSession, chat_id: int) -> Chat:
        chat = ChatModel(id=chat_id)
        db_session.add(chat)
        await db_session.flush()
        chat = Chat(id=chat.id)
        return chat

    async def add_player_to_db(self, db_session: AsyncSession, player_id: int, name: str) -> Player:
        player = PlayerModel(id=player_id, name=name)
        db_session.add(player)
        await db_session.flush()
        return Player(id=player_id, name=name)

    async def get_chat(self, db_session: AsyncSession, chat_id: int) -> Chat:
        stmt = select(ChatModel).filter(ChatModel.id == chat_id)
        result = await db_session.execute(stmt)
        chat = result.scalars().first()
        return Chat(id=chat.id) if chat else None

    async def get_current_session(self, db_session: AsyncSession, chat_id: int, state: int = None) -> Optional[
        GameSession]:
        """ By default, searches only for a running game session. A chat can have one or zero running sessions """
        stmt = select(GameSessionModel).filter(
            GameSessionModel.chat_id == chat_id)
        if state:
            stmt = stmt.filter(GameSessionModel.state == state)
        else:
            stmt = stmt.filter(GameSessionModel.state != StatesEnum.ENDED.value)
        result = await db_session.execute(stmt)
        session = result.scalars().first()
        if session:
            creator = await self.get_player_by_id(db_session, session.creator_id)
            players = await self.get_players(db_session, session.id)
            return GameSessionModel.to_dc(session, creator, players)

    async def create_session(self, db_session: AsyncSession, chat_id: int, creator_id):
        session = GameSessionModel(chat_id=chat_id, creator_id=creator_id, state=StatesEnum.PREPARING.value)
        db_session.add(session)
        await db_session.flush()
        association = PlayersSessions(player_id=creator_id, session_id=session.id)
        db_session.add(association)

    async def get_sessions(self, db_session: AsyncSession, **kwargs) -> list[GameSession]:
        stmt = select(GameSessionModel)
        for field in kwargs.keys():
            if field == "chat_id":
                stmt = stmt.filter(GameSessionModel.chat_id == kwargs[field])
            if field == "state_not":
                stmt = stmt.filter(GameSessionModel.state != kwargs[field])
        result = await db_session.execute(stmt)
        curr = result.scalars()
        game_sessions = list()
        for session in curr:
            creator = await self.get_player_by_id(db_session, session.creator_id)
            players = await self.get_players(db_session, session.id)
            game_sessions.append(GameSessionModel.to_dc(session, creator, players))
        return game_sessions

    async def get_player_by_id(self, db_session: AsyncSession, player_id: int) -> Optional[Player]:
        stmt = select(PlayerModel).filter(PlayerModel.id == player_id)
        result = await db_session.execute(stmt)
        player = result.scalars().first()
        if player:
            return Player(id=player.id, name=player.name) if player else None

    async def get_players(self, db_session: AsyncSession, session_id=None) -> List[Player]:
        stmt = select(PlayerModel)
        if session_id:
            stmt = stmt.join(PlayerModel.player_in_session).filter(
                PlayersSessions.session_id == session_id)
        result = await db_session.execute(stmt)
        curr = result.scalars()
        return [Player(id=player.id, name=player.name) for player in curr]

    async def get_session_player(self, db_session: AsyncSession, player_id: int, session_id: int) -> Optional[
        SessionPlayer]:
        stmt = select(PlayersSessions).where(
            PlayersSessions.player_id == player_id).where(
            PlayersSessions.session_id == session_id)
        result = await db_session.execute(stmt)
        session_player = result.scalars().first()
        if session_player:
            return PlayersSessions.to_dc(session_player)

    async def get_session_players(self, db_session: AsyncSession, session_id: int) -> List[SessionPlayer]:
        stmt = select(PlayersSessions).where(
            PlayersSessions.session_id == session_id)
        result = await db_session.execute(stmt)
        curr = result.scalars()
        return [PlayersSessions.to_dc(session_player) for session_player in curr]

    async def add_player_to_session(self, db_session: AsyncSession, player_id: int, session_id: int) -> None:
        association = PlayersSessions(player_id=player_id, session_id=session_id)
        db_session.add(association)

    async def assign_players_order(self, db_session: AsyncSession, session_id: int,
                                   required_order: Iterator[tuple]) -> None:
        for player, next_player in required_order:
            stmt = select(PlayersSessions).where(
                PlayersSessions.player_id == player.id).where(
                PlayersSessions.session_id == session_id)
            result = await db_session.execute(stmt)
            session_player = result.scalars().first()
            session_player.next_player_id = next_player.id

    async def set_session_state(self, db_session: AsyncSession, session_id: int, new_state: int) -> None:
        stmt = update(GameSessionModel).where(
            GameSessionModel.id == session_id).values(state=new_state)
        await db_session.execute(stmt)

    async def set_first_word(self, db_session: AsyncSession, session_id: int) -> Word:
        word = random.choice(START_WORDS) if self.app.config.game.random_start else TEST_WORD
        session_word = SessionWords(word=word, proposed_by=BOT_ID, session_id=session_id, approved=True)
        db_session.add(session_word)
        return SessionWords.to_dc(session_word)

    async def get_last_session_word(self, db_session: AsyncSession, session_id: int, approved: Optional[bool] = None) -> Optional[Word]:
        stmt = select(SessionWords).filter(
            SessionWords.session_id == session_id)
        stmt = stmt.order_by(
            SessionWords.id.desc())
        result = await db_session.execute(stmt)
        word = result.scalars().first()
        return SessionWords.to_dc(word)

    async def add_session_word(self,
                               db_session: AsyncSession,
                               player_id: int,
                               previous_word_id: int,
                               word: str,
                               session_id: int) -> Word:
        session_word = SessionWords(word=word,
                                    proposed_by=player_id,
                                    previous_word=previous_word_id,
                                    session_id=session_id)
        db_session.add(session_word)
        return SessionWords.to_dc(session_word)

    async def choose_first_player(self, db_session: AsyncSession, players: list[Player], session_id: int) -> Player:
        player = random.choice(players)
        association = PlayersSessions(player_id=BOT_ID, session_id=session_id, next_player_id=player.id)
        db_session.add(association)
        return player

    async def has_voted(self, db_session: AsyncSession, user_id: int, session_word_id: int) -> bool:
        stmt = select(WordVotes).filter(
            WordVotes.session_word == session_word_id).filter(
            WordVotes.player_id == user_id)
        result = await db_session.execute(stmt)
        existing_vote = result.scalars().first()
        if existing_vote:
            return True
        return False

    async def vote(self, db_session: AsyncSession, user_id: int, vote_message: str, session_word_id: int) -> bool:
        vote = True if vote_message == "/yes" else False

        word_vote = WordVotes(session_word=session_word_id, player_id=user_id, vote=vote)
        db_session.add(word_vote)

    async def get_word_votes(self, db_session: AsyncSession, session_word_id: int) -> List[bool]:
        stmt = select(WordVotes).filter(
            WordVotes.session_word == session_word_id)
        result = await db_session.execute(stmt)
        word_votes = result.scalars()
        return [vote.vote for vote in word_votes]

    async def set_vote_result(self, db_session: AsyncSession, session_word_id: int, vote_result: bool) -> None:
        stmt = update(SessionWords).filter(
            SessionWords.id == session_word_id).values(approved=vote_result)
        await db_session.execute(stmt)

    async def accrue_points(self, db_session: AsyncSession, player_id: int, session_id: int, word: str) -> int:
        points = judge_word(word)
        stmt = select(PlayersSessions).where(
            PlayersSessions.player_id == player_id).where(
            PlayersSessions.session_id == session_id)
        result = await db_session.execute(stmt)
        session_player = result.scalars().first()
        session_player.points += points
        return points

    async def drop_player(self, db_session: AsyncSession, player_id: int, session_id: int) -> None:
        stmt = update(PlayersSessions).filter(
            PlayersSessions.player_id == player_id).filter(
            PlayersSessions.session_id == session_id).values(is_dropped_out=True)
        await db_session.execute(stmt)


    async def get_next_player(self, db_session: AsyncSession, player_id: int, session_id: int) -> Optional[Player]:
        """ Searches for the next one player in session who is not lost yet """
        start = player_id
        session_player = await self.get_session_player(db_session, player_id, session_id)
        while True:
            print(session_player.player_id, session_player.next_player_id)
            next_player_in_session_id = session_player.next_player_id
            next_player_in_session = await self.get_session_player(db_session, next_player_in_session_id, session_id)
            player_id = next_player_in_session_id
            if not next_player_in_session.is_dropped_out:
                return await self.get_player_by_id(db_session, player_id)

            # Hope the was no situation, if all players in game session is lost. Session shouldn't be able to
            # be started with less than two players and should be ended when only one player remains
            if player_id == start:
                self.logger.error("All players is dropped from game! Can't choose the next player to propose a word")
                break
