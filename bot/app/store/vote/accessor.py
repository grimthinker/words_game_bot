from typing import List
from sqlalchemy import select, or_, and_, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game_session.models import (
    WordVotes,
)


class VoteAccessor(BaseAccessor):
    async def has_voted(
        self, db_session: AsyncSession, user_id: int, session_word_id: int
    ) -> bool:
        stmt = (
            select(WordVotes)
            .filter(WordVotes.session_word == session_word_id)
            .filter(WordVotes.player_id == user_id)
        )
        result = await db_session.execute(stmt)
        existing_vote = result.scalars().first()
        if existing_vote:
            return True
        return False

    async def vote(
        self,
        db_session: AsyncSession,
        user_id: int,
        vote_message: str,
        session_word_id: int,
    ) -> None:
        vote = True if vote_message == "/yes" else False

        word_vote = WordVotes(
            session_word=session_word_id, player_id=user_id, vote=vote
        )
        db_session.add(word_vote)

    async def get_word_votes(
        self, db_session: AsyncSession, session_word_id: int
    ) -> List[bool]:
        stmt = select(WordVotes).filter(WordVotes.session_word == session_word_id)
        result = await db_session.execute(stmt)
        word_votes = result.scalars()
        return [vote.vote for vote in word_votes]
