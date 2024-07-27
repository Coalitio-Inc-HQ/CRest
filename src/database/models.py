from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, CheckConstraint, text, ForeignKey, JSON
from datetime import datetime


class Base(DeclarativeBase):
    pass


class AuthORM(Base):
    __tablename__ = "auth"
    access_token: Mapped[str]
    expires_in: Mapped[int]
    refresh_token: Mapped[str]
    client_endpoint: Mapped[str]
    member_id:Mapped[str] = mapped_column(primary_key=True)
    application_token: Mapped[str] = mapped_column(nullable=True)
    placement_options:Mapped[dict] = mapped_column(JSON, nullable=True)

    # AUTH_ID: Mapped[str]
    # AUTH_EXPIRES:Mapped[int]
    # REFRESH_ID:Mapped[str]
    # member_id:Mapped[str] = mapped_column(primary_key=True)
    # status:Mapped[str]
    # PLACEMENT:Mapped[str]
    # PLACEMENT_OPTIONS:Mapped[dict] = mapped_column(JSON)

