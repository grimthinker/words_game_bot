import random
from typing import Optional, Union, Iterator, Iterable, List
from sqlalchemy import select, or_, and_, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game_session.models import (
    GameSessionModel,
    GameSession,
    StatesEnum,
    PlayersSessions,
)


class GameSessionAccessor(BaseAccessor):
    async def get_current_session(
        self, db_session: AsyncSession, chat_id: int, state: int = None
    ) -> Optional[GameSession]:
        """By default, searches only for a running game session. A chat can have one or zero running sessions"""
        stmt = select(GameSessionModel).filter(GameSessionModel.chat_id == chat_id)
        if state:
            stmt = stmt.filter(GameSessionModel.state == state)
        else:
            stmt = stmt.filter(GameSessionModel.state != StatesEnum.ENDED.value)
        result = await db_session.execute(stmt)
        session = result.scalars().first()
        if session:
            creator = await self.app.store.players.get_player_by_id(
                db_session, session.creator_id
            )
            players = await self.app.store.players.get_players(db_session, session.id)
            return GameSessionModel.to_dc(session, creator, players)

    async def create_session(self, db_session: AsyncSession, chat_id: int, creator_id):
        session = GameSessionModel(
            chat_id=chat_id, creator_id=creator_id, state=StatesEnum.PREPARING.value
        )
        db_session.add(session)
        await db_session.flush()
        association = PlayersSessions(player_id=creator_id, session_id=session.id)
        db_session.add(association)

    async def get_sessions(
        self, db_session: AsyncSession, **kwargs
    ) -> list[GameSession]:
        stmt = select(GameSessionModel)
        if kwargs.get("chat_id"):
            stmt = stmt.filter(GameSessionModel.chat_id == kwargs.get("chat_id"))
        if kwargs.get("state_not"):
            stmt = stmt.filter(GameSessionModel.state != kwargs.get("state_not"))
        result = await db_session.execute(stmt)
        curr = result.scalars()
        game_sessions = list()
        for session in curr:
            creator = await self.app.store.players.get_player_by_id(
                db_session, session.creator_id
            )
            players = await self.app.store.players.get_players(db_session, session.id)
            game_sessions.append(GameSessionModel.to_dc(session, creator, players))
        return game_sessions

    async def set_session_state(
        self, db_session: AsyncSession, session_id: int, new_state: int
    ) -> None:
        stmt = (
            update(GameSessionModel)
            .where(GameSessionModel.id == session_id)
            .values(state=new_state)
        )
        await db_session.execute(stmt)
