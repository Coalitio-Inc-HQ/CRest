from .models import *
from .schemes import *

from sqlalchemy import select, insert, text, func, bindparam, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

async def insert_auth(session: AsyncSession, auth: AuthDTO) -> None:
    """
    Проверяет есть ли AuthDTO и сохраняет или обновляет AuthDTO в БД.
    """
    print("axasdasasdsaasddasadsasdasd")
    print(auth)
    res_orm = (await session.execute(select(AuthORM).where(AuthORM.member_id==auth.member_id))).all()
    if (len(res_orm)==0):
        session.add(AuthORM(access_token = auth.access_token,
                            expires_in = auth.expires_in,
                            refresh_token = auth.refresh_token,
                            client_endpoint = auth.client_endpoint,
                            member_id = auth.member_id,
                            application_token = auth.application_token,
                            placement_options = auth.placement_options
                            ))
    else:
        await session.execute(update(AuthORM).where(AuthORM.member_id==auth.member_id).values(
                                                                                                access_token = auth.access_token,
                                                                                                expires_in = auth.expires_in,
                                                                                                refresh_token = auth.refresh_token,
                                                                                                client_endpoint = auth.client_endpoint,
                                                                                                member_id = auth.member_id,
                                                                                                application_token = auth.application_token,
                                                                                                placement_options = auth.placement_options
                                                                                                ))
    await session.commit()


async def update_auth(session: AsyncSession, member_id: str, access_token: str, expires_in: int, client_endpoint: str, refresh_token: str) -> None:
    """
    Используется для обновления AuthDTO после использования refresh_token.
    """
    await session.execute(update(AuthORM).where(AuthORM.member_id==member_id).values(
                                                                                                access_token = access_token,
                                                                                                expires_in = expires_in,
                                                                                                refresh_token = refresh_token,
                                                                                                client_endpoint = client_endpoint,
                                                                                                member_id = member_id,
                                                                                                ))
    
    await session.commit()

async def get_auth_by_member_id(session: AsyncSession, member_id: str) -> AuthDTO:
    """
    Получает AuthDTO из БД по member_id.
    """
    res_orm = (await session.execute(select(AuthORM).where(AuthORM.member_id==member_id))).scalar()
    return AuthDTO.model_validate(res_orm,from_attributes=True)