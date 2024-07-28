
from src.database.session_database import engine, session_factory
import asyncio

from src.call.calls import call_batch_web_hook

from src.database.database_requests import *

from sqlalchemy import text

async def run():
    arr = []
    for i in range(46):
        arr.append(
            {
                "method": "crm.contact.add",
                "params":{
                    "FIELDS":{
                        "NAME":f"Иван{i}",
                        "LAST_NAME":f"Петров{i}"
                    }
                }
            }
        )

    arr.insert(10,
            {
                "method": "crm.contact.add",
                "params":{
                    "FIELDS":"NAME"
                }
            }
        )

    print(await call_batch_web_hook(
        arr,True
    ))


asyncio.run(run())