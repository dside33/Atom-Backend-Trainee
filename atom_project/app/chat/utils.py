from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.chat.models import Chat
from app.auth.models import User


async def verify_user_belongs_to_chat(chat_id: int, user: User, db: AsyncSession):
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()

    if not chat or (chat.user1_id != user.id and chat.user2_id != user.id):
        return False
    return True
