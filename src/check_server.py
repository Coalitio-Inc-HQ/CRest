from src.settings import settings
from src.loging.logging_utility import log, LogMessage,log_en
from src.database.session_database import engine
from sqlalchemy import text

import asyncio

if settings.C_REST_WEB_HOOK_URL == "" and (settings.C_REST_CLIENT_ID=="" or settings.C_REST_CLIENT_SECRET==""):
    log(LogMessage(time=None,heder="Ошибка в env неопредены параметры CRest.", 
                heder_dict={},body=
                {},
                level=log_en.ERROR))
    raise Exception()


async def test_db():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT version();")) 

try:
    asyncio.run(test_db())
except:
    log(LogMessage(time=None,heder="Ошибка подключения к базе данныхю.", 
                heder_dict={},body=
                {},
                level=log_en.ERROR))
    raise Exception()

log(LogMessage(time=None,heder="Проверка пройдена успешно.", 
                heder_dict={},body=
                {},
                level=log_en.INFO))