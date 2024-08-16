from CRest.settings import settings
from CRest.database.session_database import session_factory
from sqlalchemy import text

import asyncio

from CRest.loging.logging_utility import log, LogMessage, LogHeader,log_en
import uuid
import traceback


if settings.C_REST_WEB_HOOK_URL == "" and (settings.C_REST_CLIENT_ID=="" or settings.C_REST_CLIENT_SECRET==""):
    log(
        LogMessage(
            header=LogHeader(
                    id = uuid.uuid4(),
                    title = "Ошибка в env неопредены параметры CRest.",
                    tegs = {},
                    time = None,
                    level = log_en.ERROR
            ),
            body = {}
        )
    )
    raise Exception()


async def test_db():
    async with session_factory() as conn:
        await conn.execute(text("SELECT version()")) 

try:
    asyncio.run(test_db())
except:
    log(
        LogMessage(
            header=LogHeader(
                    id = uuid.uuid4(),
                    title = "Ошибка подключения к базе данных.",
                    tegs = {},
                    time = None,
                    level = log_en.ERROR
            ),
            body = {}
        )
    )
    raise Exception()


log(
    LogMessage(
        header=LogHeader(
                id = uuid.uuid4(),
                title = "Проверка пройдена успешно.",
                tegs = {},
                time = None,
                level = log_en.INFO
        ),
        body = {}
    )
)
