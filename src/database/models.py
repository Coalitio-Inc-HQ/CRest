from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, CheckConstraint, text, ForeignKey, JSON
from datetime import datetime


class Base(DeclarativeBase):
    pass


class AuthORM(Base):
    __tablename__ = "auth"

    lang: Mapped[str]
    app_id: Mapped[str]

    access_token: Mapped[str]
    expires: Mapped[int | None]
    expires_in: Mapped[int]
    scope: Mapped[str | None]
    domain: Mapped[str]
    status: Mapped[str]
    member_id: Mapped[str | None] = mapped_column(primary_key=True)
    user_id: Mapped[int | None]
    refresh_token: Mapped[str]
