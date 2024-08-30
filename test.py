from CRest.database.session_database import engine, session_factory
import asyncio

from CRest.call.calls import CallAPIBitrix
from CRest.call.call_director import CallDirectorBarrelStrategy

from CRest.call.url_builders.base_url_builders.web_hook_url_builder import WebHookUrlBuilder

from CRest.database.database_requests import *

from sqlalchemy import text

import base64

async def run():

    web_hook_url_builder = WebHookUrlBuilder("web_hook_settings.json")

    bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())

    with open("C:\\Users\\vl\\Desktop\\1.docx", "rb") as file:

        res = await bitrix_api.call_method(web_hook_url_builder, "documentgenerator.template.add",
                                        {
                                            "FIELDS":{
                                                "NAME":f"Rest Template",
                                                "file":base64.b64encode(file.read()),
                                                "numeratorId": 36,
                                                "providers":[
                                                    'Bitrix\\DocumentGenerator\\DataProvider\\Rest'
                                                ]
                                            }
                                        }
                                        )
        print(res)


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
    # Тест operating
    # while True:  
    #     arr = []
    #     for i in range(20):  
    #         arr.append(
    #             {
    #                 "method": "crm.contact.add",
    #                 "params":{
    #                     "FIELDS":{
    #                         "NAME":f"Иванко{i}",
    #                         "LAST_NAME":f"Петрович{i}"
    #                     }
    #                 }
    #             }
    #         )

    #     try:
    #         res1 = await bitrix_api.call_batch(web_hook_url_builder, arr)
    #         print(res1)
    #     except Exception as e:
    #         print(f"Exception occurred: {e}")



    # for i in range(1):
    #     arr = []
    #     for i in range(3):
    #         arr.append(
    #             {
    #                 "method": "crm.contact.add",
    #                 "params":{
    #                     "FIELDS":{
    #                         "NAME":f"Иван{i}",
    #                         "LAST_NAME":f"Петров{i}"
    #                     }
    #                 }
    #             }
    #         )

    #     # arr.insert(50,
    #     #         {
    #     #             "method": "crm.contac1t.add",
    #     #             "params":{
    #     #                 "FIELDS":{
    #     #                     "NAME":f"Иван{i}",
    #     #                     "LAST_NAME":f"Петров{i}"
    #     #                 }
    #     #             }
    #     #         }
    #     #     )

    #     res1 = await bitrix_api.call_batch(web_hook_url_builder,arr)
    #     print(res1)


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