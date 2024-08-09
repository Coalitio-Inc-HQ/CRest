from src.database.session_database import engine, session_factory
import asyncio

from src.call.calls import call_method, call_batch, get_list, get_list_bath, get_list_generator
from src.call.url_builder import web_hook_url_builder

from src.database.database_requests import *

from sqlalchemy import text

async def run():
    # for x in range(2600):
    #   res = await call_method(web_hook_url_builder, "crm.contact.add",
    #                                   {
    #                                     "FIELDS":{
    #                                           "NAME":f"Иван",
    #                                           "LAST_NAME":f"Петров"
    #                                       }
    #                                   }
    #                                 )
    #   print(res)

    for i in range(1000):
        arr = []
        for i in range(100):
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

        # arr.insert(50,
        #         {
        #             "method": "crm.contac1t.add",
        #             "params":{
        #                 "FIELDS":{
        #                     "NAME":f"Иван{i}",
        #                     "LAST_NAME":f"Петров{i}"
        #                 }
        #             }
        #         }
        #     )

        res1 = await call_batch(web_hook_url_builder,arr)
        print(res1)


    # lis = await get_list( web_hook_url_builder,"crm.contact.list")
    # print (len(lis))
    # for item in lis:
    #     print(item)

    # lis1 = await get_list_bath( web_hook_url_builder,"crm.contact.list")
    # print (len(lis1))
    # for item in lis1:
    #     print(item)

    # count = 0 
    # async for item in get_list_generator( web_hook_url_builder,"crm.contact.list"):
    #     print(item)
    #     count +=1
    # print(count)

    # for i in range(50):
    #     arr=[]
    #     count = 0
    #     async for item in get_list_generator( web_hook_url_builder,"crm.contact.list"):
    #         arr.append(
    #             {
    #                 "method": "crm.contact.delete",
    #                 "params":{
    #                     "ID": str(item["ID"])
    #                 }
    #             }
    #         )
    #         count+=1
    #         print(count)
    #         if count == 45:
    #             break
    #     print(await call_batch(web_hook_url_builder, arr))

asyncio.run(run())