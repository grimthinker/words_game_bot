import random
from typing import Optional, Iterator, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    PlayerModel,
    Player,
    PlayersSessions,
    SessionPlayer,
)
from app.store.bot.constants import BOT_ID, BOT_NAME, START_WORDS, TEST_WORD


class PlayerAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        async with self.app.database.session() as db_session:
            await self.add_player_to_db(db_session, BOT_ID, BOT_NAME)

            await db_session.commit()

    async def add_player_to_db(
        self, db_session: AsyncSession, player_id: int, name: str
    ) -> Player:
        player = PlayerModel(id=player_id, name=name)
        db_session.add(player)
        await db_session.flush()
        return Player(id=player_id, name=name)

    async def get_player_by_id(
        self, db_session: AsyncSession, player_id: int
    ) -> Optional[Player]:
        stmt = select(PlayerModel).filter(PlayerModel.id == player_id)
        result = await db_session.execute(stmt)
        player = result.scalars().first()
        return Player(id=player.id, name=player.name) if player else None

    async def get_players(
        self, db_session: AsyncSession, session_id=None
    ) -> List[Player]:
        stmt = select(PlayerModel)
        if session_id:
            stmt = stmt.join(PlayerModel.player_in_session).filter(
                PlayersSessions.session_id == session_id
            )
        result = await db_session.execute(stmt)
        curr = result.scalars()
        return [Player(id=player.id, name=player.name) for player in curr]

    async def get_session_player(
        self, db_session: AsyncSession, player_id: int, session_id: int
    ) -> Optional[SessionPlayer]:
        stmt = (
            select(PlayersSessions)
            .where(PlayersSessions.player_id == player_id)
            .where(PlayersSessions.session_id == session_id)
        )
        result = await db_session.execute(stmt)
        session_player = result.scalars().first()
        return PlayersSessions.to_dc(session_player) if session_player else None

    async def get_session_players(
        self, db_session: AsyncSession, session_id: int
    ) -> List[SessionPlayer]:
        stmt = select(PlayersSessions).where(PlayersSessions.session_id == session_id)
        result = await db_session.execute(stmt)
        curr = result.scalars()
        return [PlayersSessions.to_dc(session_player) for session_player in curr]

    async def add_player_to_session(
        self, db_session: AsyncSession, player_id: int, session_id: int
    ) -> None:
        association = PlayersSessions(player_id=player_id, session_id=session_id)
        db_session.add(association)

    async def assign_players_order(
        self, db_session: AsyncSession, session_id: int, required_order: Iterator[tuple]
    ) -> None:
        for player, next_player in required_order:
            stmt = (
                select(PlayersSessions)
                .where(PlayersSessions.player_id == player.id)
                .where(PlayersSessions.session_id == session_id)
            )
            result = await db_session.execute(stmt)
            session_player = result.scalars().first()
            session_player.next_player_id = next_player.id

    async def choose_first_player(
        self, db_session: AsyncSession, players: list[Player], session_id: int
    ) -> Player:
        player = random.choice(players)
        association = PlayersSessions(
            player_id=BOT_ID, session_id=session_id, next_player_id=player.id
        )
        db_session.add(association)
        return player

    async def accrue_points(
        self, db_session: AsyncSession, player_id: int, session_id: int, points: int
    ) -> None:
        stmt = (
            select(PlayersSessions)
            .where(PlayersSessions.player_id == player_id)
            .where(PlayersSessions.session_id == session_id)
        )
        result = await db_session.execute(stmt)
        session_player = result.scalars().first()
        session_player.points += points

    async def drop_player(
        self, db_session: AsyncSession, player_id: int, session_id: int
    ) -> None:

        stmt = (
            select(PlayersSessions)
            .where(PlayersSessions.player_id == player_id)
            .where(PlayersSessions.session_id == session_id)
        )
        result = await db_session.execute(stmt)
        session_player = result.scalars().first()
        session_player.lives -= 1
        if session_player.lives == 0:
            session_player.is_dropped_out = True

    async def get_next_player(
        self, db_session: AsyncSession, player_id: int, session_id: int
    ) -> Optional[Player]:
        """Searches for the next one player in session who is not lost yet"""
        start = player_id
        session_player = await self.get_session_player(
            db_session, player_id, session_id
        )
        while True:
            next_player_in_session_id = session_player.next_player_id
            next_player_in_session = await self.get_session_player(
                db_session, next_player_in_session_id, session_id
            )
            player_id = next_player_in_session_id
            if not next_player_in_session.is_dropped_out:
                return await self.get_player_by_id(db_session, player_id)

            # Hope the was no situation, if all players in game session is lost. Session shouldn't be able to
            # be started with less than two players and should be ended when only one player remains
            if player_id == start:
                self.logger.error(
                    "All players is dropped from game! Can't choose the next player to propose a word"
                )
                break
