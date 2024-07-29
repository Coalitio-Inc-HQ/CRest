
from src.database.session_database import engine, session_factory
import asyncio

from src.call.calls import call_method, call_batch, get_list
from src.call.url_builder import web_hook_url_builder

from src.database.database_requests import *

from sqlalchemy import text

async def run():
    # res = await call_method(web_hook_url_builder, "crm.contact.add",
    #                                 {
    #                                   "FIELDS":{
    #                                         "NAME":f"Иван",
    #                                         "LAST_NAME":f"Петров"
    #                                     }
    #                                 }
    #                               )
    # print(res)

    # arr = []
    # for i in range(46):
    #     arr.append(
    #         {
    #             "method": "crm.contact.add",
    #             "params":{
    #                 "FIELDS":{
    #                     "NAME":f"Иван{i}",
    #                     "LAST_NAME":f"Петров{i}"
    #                 }
    #             }
    #         }
    #     )

    # arr.insert(10,
    #         {
    #             "method": "crm.contact.add",
    #             "params":{
    #                 "FIELDS":"NAME"
    #             }
    #         }
    #     )

    # res1 = await call_batch(web_hook_url_builder,arr,)
    # print(res1)


    lis = await get_list( web_hook_url_builder,"crm.contact.list", {
        "order":{
            "ID":"DESC"
        },
        "filter": {
            ">ID":"1862"
        }
    })
    print (len(lis))
    for item in lis:
        print(item)

asyncio.run(run())