import random
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    SessionWords,
    Word,
    WordVotes,
)
from app.store.bot.constants import BOT_ID, BOT_NAME, START_WORDS, TEST_WORD


class WordAccessor(BaseAccessor):
    async def set_first_word(self, db_session: AsyncSession, session_id: int) -> Word:
        word = (
            random.choice(START_WORDS)
            if self.app.config.game.random_start
            else TEST_WORD
        )
        session_word = SessionWords(
            word=word, proposed_by=BOT_ID, session_id=session_id, approved=True
        )
        db_session.add(session_word)
        return SessionWords.to_dc(session_word)

    async def get_last_session_word(
        self,
        db_session: AsyncSession,
        session_id: int,
        text: Optional[str] = None,
        approved: Optional[bool] = None,
    ) -> Optional[Word]:
        stmt = (
            select(SessionWords)
            .filter(SessionWords.session_id == session_id)
            .filter(SessionWords.approved == approved)
        )
        if text:
            stmt = stmt.filter(SessionWords.word == text)
        stmt = stmt.order_by(SessionWords.id.desc())
        result = await db_session.execute(stmt)
        word = result.scalars().first()
        return SessionWords.to_dc(word) if word else None

    async def add_session_word(
        self,
        db_session: AsyncSession,
        player_id: int,
        previous_word_id: int,
        word: str,
        session_id: int,
    ) -> Word:
        session_word = SessionWords(
            word=word,
            proposed_by=player_id,
            previous_word=previous_word_id,
            session_id=session_id,
        )
        db_session.add(session_word)
        return SessionWords.to_dc(session_word)

    async def set_vote_result(
        self, db_session: AsyncSession, session_word_id: int, vote_result: bool
    ) -> None:
        stmt = (
            update(SessionWords)
            .filter(SessionWords.id == session_word_id)
            .values({"approved": vote_result})
        )
        await db_session.execute(stmt)
