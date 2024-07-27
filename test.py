
from src.database.session_database import engine, session_factory
import asyncio

from src.call.calls import call_batch_web_hook

from src.database.database_requests import *

from sqlalchemy import text

async def run():
    # print(await call_batch_web_hook(
    #     [
    #         {
    #             "method": "crm.contact.add",
    #             "params":{
    #                 "FIELDS":{
    #                     "NAME":"Иван1",
    #                     "LAST_NAME":"Петров1"
    #                 }
    #             }
    #         },
    #         {
    #             "method": "crm.contact.add",
    #             "params":{
    #                 "FIELDS":{
    #                     "NAME":"Иван2",
    #                     "LAST_NAME":"Петров2"
    #                 }
    #             }
    #         }
    #     ]
    # ))
    async with session_factory() as conn:
        auth_dict ={'AUTH_ID': '2fb0a466006fec30006fdb0400000001605407fb2e3b2690bb81c8373b7ba70091c692', 'AUTH_EXPIRES': '3600', 'REFRESH_ID': '1f2fcc66006fec30006fdb04000000016054073aacba93d8ccbc2936e578f775fe40a7', 'member_id': '491a9e9c74d4f68354289940ba405024', 'status': 'F', 'PLACEMENT': 'DEFAULT', 'PLACEMENT_OPTIONS': {'any': '15/'}}

        await insert_auth(conn, AuthDTO(
            access_token = "abbca466006fec30006fdb04000000016054070ee7f4c264d3d5707e7cb34a56b970b1",
            expires_in = 3600 ,
            refresh_token = "9c3bcc66006fec30006fdb04000000016054076991dc310c7995f566fa4ad9c4265433",
            client_endpoint = "https://b24-gqynk1.bitrix24.ru/rest/",
            member_id = "491a9e9c74d4f68354289940ba405024",
            application_token = "71f7ed726034331ecd4ea30330958df0",
            placement_options = {'any': '15/'}
        ))


asyncio.run(run())