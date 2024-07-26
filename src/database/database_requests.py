from .models import *
from .schemes import *

from sqlalchemy import select, insert, text, func, bindparam, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

async def insert_auth(session: AsyncSession, auth: AuthDTO) -> None:
    """
    Сохраняет AuthDTO в БД.
    """
    session.add(AuthORM(AUTH_ID=auth.AUTH_ID,
                        AUTH_EXPIRES=auth.AUTH_EXPIRES,
                        REFRESH_ID=auth.REFRESH_ID,
                        member_id=auth.member_id,
                        status=auth.status,
                        PLACEMENT=auth.PLACEMENT,
                        PLACEMENT_OPTIONS=auth.PLACEMENT_OPTIONS,
                        ))
    await session.commit()


async def get_auth_by_member_id(session: AsyncSession, member_id: str) -> AuthDTO:
    """
    Получает AuthDTO из БД по member_id.
    """
    res_orm = (await session.execute(select(AuthORM).where(AuthORM.member_id==member_id))).scalar()
    return AuthDTO.model_validate(res_orm,from_attributes=True)