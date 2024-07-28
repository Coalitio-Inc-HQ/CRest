
from src.database.session_database import engine, session_factory
import asyncio

from src.call.calls import call_batch_web_hook, call_url_web_hook, get_list_web_hook

from src.database.database_requests import *

from sqlalchemy import text

async def run():
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

    # print(await call_batch_web_hook(
    #     [
    #         {
    #             "method": "crm.contact.add",
    #             "params":{
    #                 "FIELDS":{
    #                     "NAME":f"Иван",
    #                     "LAST_NAME":f"Петров"
    #                 }
    #             }
    #         },
    #         {
    #             "method": "crm.contact.get",
    #             "params":{
    #                 "ID": "$result[1]"
    #             }
    #         },
    #         {
    #             "method": "crm.contact.list",
    #             "params":{
                    
    #             }
    #         },
    #         {
    #             "method": "crm.contact.list",
    #             "params":{
                    
    #             }
    #         },
    #     ]
    #     ,True
    # ))

    # res = await call_url_web_hook("crm.contact.add",
    #                                 {
    #                                   "FIELDS":{
    #                                         "NAME":f"Иван",
    #                                         "LAST_NAME":f"Петров"
    #                                     }
    #                                 }
    #                               )

    # res = await call_url_web_hook("crm.contact.get",
    #                                 {
    #                                   "ID":1645
    #                                 }
    #                               )

    # print(res)

    lis = await get_list_web_hook("crm.contact.list", {
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