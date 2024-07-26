from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, CheckConstraint, text, ForeignKey, JSON
from datetime import datetime


class Base(DeclarativeBase):
    pass


class AuthORM(Base):
    __tablename__ = "auth"
    AUTH_ID: Mapped[str]
    AUTH_EXPIRES:Mapped[int]
    REFRESH_ID:Mapped[str]
    member_id:Mapped[str] = mapped_column(primary_key=True)
    status:Mapped[str]
    PLACEMENT:Mapped[str]
    PLACEMENT_OPTIONS:Mapped[dict] = mapped_column(JSON)

