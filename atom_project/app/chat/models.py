from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey

from datetime import datetime

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    user1_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user2_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user1: Mapped["User"] = relationship("User", foreign_keys=[user1_id])
    user2: Mapped["User"] = relationship("User", foreign_keys=[user2_id])
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat")
