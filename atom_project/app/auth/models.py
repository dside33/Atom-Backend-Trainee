from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, Boolean, Enum

from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base


class UserRole(PyEnum):
    MODERATOR = "moderator"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    can_write: Mapped[bool] = mapped_column(Boolean, default=True)
