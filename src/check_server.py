from src.settings import settings
from src.loging.logging_utility import log, LogMessage,log_en
from src.database.session_database import session_factory
from sqlalchemy import text

import asyncio

if settings.C_REST_WEB_HOOK_URL == "" and (settings.C_REST_CLIENT_ID=="" or settings.C_REST_CLIENT_SECRET==""):
    log(LogMessage(time=None,header="Ошибка в env неопредены параметры CRest.", 
                header_dict={},body=
                {},
                level=log_en.ERROR))
    raise Exception()


async def test_db():
    async with session_factory() as conn:
        await conn.execute(text("SELECT version()")) 

try:
    asyncio.run(test_db())
except:
    log(LogMessage(time=None,header="Ошибка подключения к базе данныхю.", 
                header_dict={},body=
                {},
                level=log_en.ERROR))
    raise Exception()

log(LogMessage(time=None,header="Проверка пройдена успешно.", 
                header_dict={},body=
                {},
                level=log_en.INFO))