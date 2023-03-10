from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    ChatModel,
    Chat,
)


class ChatAccessor(BaseAccessor):
    async def add_chat_to_db(self, db_session: AsyncSession, chat_id: int) -> Chat:
        chat = ChatModel(id=chat_id)
        db_session.add(chat)
        await db_session.flush()
        chat = Chat(id=chat.id)
        return chat

    async def get_chat(self, db_session: AsyncSession, chat_id: int) -> Optional[Chat]:
        stmt = select(ChatModel).filter(ChatModel.id == chat_id)
        result = await db_session.execute(stmt)
        chat = result.scalars().first()
        return Chat(id=chat.id) if chat else None
