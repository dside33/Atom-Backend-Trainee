from sqlalchemy.future import select
import asyncio

from app.core.database import AsyncSessionLocal
from app.auth.models import User, UserRole
from app.chat.models import Chat


async def create_test_users_and_chats():
    async with AsyncSessionLocal() as db:
        users_data = [
            {
                "name": "st_user1",
                "email": "st_user1@example.com",
                "password": "pass123",
                "role": UserRole.USER,
                "can_write": True,
            },
            {
                "name": "st_user2",
                "email": "st_user2@example.com",
                "password": "pass123",
                "role": UserRole.USER,
                "can_write": True,
            },
            {
                "name": "st_user3",
                "email": "st_user3@example.com",
                "password": "pass123",
                "role": UserRole.USER,
                "can_write": True,
            },
            {
                "name": "mod_user",
                "email": "mod_user@example.com",
                "password": "pass123",
                "role": UserRole.MODERATOR,
                "can_write": True,
            },
        ]

        user_objects = {}
        for user_data in users_data:
            result = await db.execute(select(User).where(User.email == user_data["email"]))
            existing_user = result.scalars().first()

            if existing_user is None:
                new_user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password=user_data["password"],
                    role=user_data["role"],
                    can_write=user_data["can_write"],
                )
                db.add(new_user)
                await db.flush()
                user_objects[user_data["email"]] = new_user
            else:
                user_objects[user_data["email"]] = existing_user

        chat_pairs = [
            ("st_user1@example.com", "st_user2@example.com"),
            ("st_user2@example.com", "st_user3@example.com"),
        ]

        for user_email_1, user_email_2 in chat_pairs:
            user1 = user_objects[user_email_1]
            user2 = user_objects[user_email_2]

            result = await db.execute(
                select(Chat).where(
                    (Chat.user1_id == user1.id and Chat.user2_id == user2.id)
                    | (Chat.user1_id == user2.id and Chat.user2_id == user1.id)
                )
            )
            existing_chat = result.scalars().first()

            if existing_chat is None:
                new_chat = Chat(user1_id=user1.id, user2_id=user2.id)
                db.add(new_chat)

        await db.commit()


if __name__ == "__main__":
    asyncio.run(create_test_users_and_chats())
