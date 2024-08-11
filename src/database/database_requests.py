from .models import *
from .schemes import *

from sqlalchemy import select, insert, text, func, bindparam, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

async def insert_auth(session: AsyncSession, auth: AuthDTO) -> None:
    """
    Проверяет есть ли AuthDTO и сохраняет или обновляет AuthDTO в БД.
    """
    res_orm = (await session.execute(select(AuthORM).where(AuthORM.member_id==auth.member_id))).all()
    if (len(res_orm)==0):
        session.add(AuthORM(lang = auth.lang,
                            app_id = auth.app_id,
                            access_token = auth.access_token,
                            expires = auth.expires,
                            expires_in = auth.expires_in,
                            scope = auth.scope,
                            domain = auth.domain,
                            status = auth.status,
                            member_id = auth.member_id,
                            user_id = auth.user_id,
                            refresh_token = auth.refresh_token
                            ))
    else:
        await session.execute(update(AuthORM).where(AuthORM.member_id==auth.member_id).values(
                                                                                                lang = auth.lang,
                                                                                                app_id = auth.app_id,
                                                                                                access_token = auth.access_token,
                                                                                                expires = auth.expires,
                                                                                                expires_in = auth.expires_in,
                                                                                                scope = auth.scope,
                                                                                                domain = auth.domain,
                                                                                                status = auth.status,
                                                                                                user_id = auth.user_id,
                                                                                                refresh_token = auth.refresh_token
                                                                                                ))
    await session.commit()


async def update_auth(session: AsyncSession, 
                    access_token: str,
                    expires: int | None,
                    expires_in: int,
                    scope: str | None,
                    domain: str,
                    status: str,
                    member_id: str | None,
                    user_id: int | None,
                    refresh_token: str
                    ) -> None:
    """
    Используется для обновления AuthDTO после использования refresh_token.
    """
    await session.execute(update(AuthORM).where(AuthORM.member_id==member_id).values(
                                                                                    access_token = access_token,
                                                                                    expires = expires,
                                                                                    expires_in = expires_in,
                                                                                    scope = scope,
                                                                                    domain = domain,
                                                                                    status = status,
                                                                                    user_id = user_id,
                                                                                    refresh_token = refresh_token
                                                                                    ))
    
    await session.commit()


async def update_auth_domain(session: AsyncSession, member_id: str, domain: str) -> None:
    """
    Используется для обновления client_endpoint в AuthDTO.
    """
    await session.execute(update(AuthORM).where(AuthORM.member_id==member_id).values(
                                                                                    client_endpoint = domain,
                                                                                    member_id = member_id,
                                                                                    ))
    
    await session.commit()


async def get_auth_by_member_id(session: AsyncSession, member_id: str) -> AuthDTO:
    """
    Получает AuthDTO из БД по member_id.
    """
    res_orm = (await session.execute(select(AuthORM).where(AuthORM.member_id==member_id))).scalar()
    return AuthDTO.model_validate(res_orm,from_attributes=True)