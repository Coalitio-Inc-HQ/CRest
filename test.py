
from src.database.session_database import engine, session_factory
import asyncio

from src.call.calls import call_batch_web_hook

from src.database.database_requests import *

from sqlalchemy import text

async def run():
    print(await call_batch_web_hook(
        [
            {
                "method": "crm.contact.add",
                "params":{
                    "FIELDS":{
                        "NAME":"Иван1",
                        "LAST_NAME":"Петров1"
                    }
                }
            },
            {
                "method": "crm.contact.add",
                "params":{
                    "FIELDS":{
                        "NAME":"Иван2",
                        "LAST_NAME":"Петров2"
                    }
                }
            }
        ]
    ))


asyncio.run(run())