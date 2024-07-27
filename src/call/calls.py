from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder,call_parameters_encoder_bath
from ..utils import send_http_post_request
from src.database.schemes import AuthDTO
from src.database.database_requests import update_auth, AsyncSession
from src.settings import settings

from httpx import HTTPStatusError

from src.loging.logging_utility import log, LogMessage,log_en

from typing import Any


"""
ToDo
Надо try except оформмить по лучше.
"""


class ExceptionRefreshAuth(Exception):
    pass

class ExceptionCallError(Exception):
    error: str

async def call_url_web_hook(method:str, params:dict) -> Any:
    """
    Осуществляет выполнение запроса через web hook.
    """

    url=f"{settings.C_REST_WEB_HOOK_URL}/{method}.json"+"?"+call_parameters_encoder(params)

    try:
        res = await send_http_post_request(url,None)
        # добавить логику работы с огрничениями (очередь)

        if "error" in res:
            log(LogMessage(time=None,heder="Ошибка при выполнении call_url_web_hook.", 
                        heder_dict={"res":res, "method":method, "params": params},body=
                        {},
                        level=log_en.ERROR))
            raise ExceptionCallError(error=res["error"])

        return res
    
    except ExceptionCallError as error:
        raise error
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении call_url_web_hook.", 
                   heder_dict=error.args,body=
                   {"method":method, "params": params},
                    level=log_en.ERROR))
        raise ExceptionCallError(error="undefined")


async def call_url_сirculation_application(method:str, params:dict, auth: AuthDTO, session: AsyncSession) -> Any:
    """
    Осуществляет выполнение запроса через app.
    """
    params_temp = params
    params_temp["auth"] = auth.access_token

    url=f"{auth.client_endpoint}{method}.json"+"?"+call_parameters_encoder(params_temp)
    try:
        res = await send_http_post_request(url,None)
        # добавить логику работы с огрничениями (очередь)

        if "error" in res:
            match res["error"]:
                case "expired_token":
                    recall_url_сirculation_application(method, params, auth, session)
                case _:
                    log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application.", 
                        heder_dict={"res":res, "method":method, "params": params},body=
                        {"auth":auth.model_dump()},
                        level=log_en.ERROR))
                    raise ExceptionCallError(error=res["error"])
        return res

    except ExceptionCallError as error:
        raise error
    except HTTPStatusError as error: # может возникнуть если пользователь сменил домен
        if error.response.status_code == 403:
            recall_url_сirculation_application(method, params, auth, session)# повторная аутентификация полчит новый адресс
        else:
            raise ExceptionCallError(error="not_found")
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application.", 
                   heder_dict=error.args,body=
                   {"auth":auth.model_dump(),"method":method, "params": params},
                    level=log_en.ERROR))
        raise ExceptionCallError(error="undefined")


async def recall_url_сirculation_application(method:str, params:dict, auth: AuthDTO, session: AsyncSession) -> Any:
    """
    Перевызов функции с повторной аутентификацией.
    """
    try:
        new_auth = await refresh_auth(auth, session)

        params_temp = params
        params_temp["auth"] = new_auth["access_token"]

        new_url=f"{new_auth["client_endpoint"]}{method}.json"+"?"+call_parameters_encoder(params_temp)
        # добавить логику работы с огрничениями (очередь)

        new_res =  await send_http_post_request(new_url,None)

        if "error" in new_res:
            log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application в блоке new_auth.", 
                heder_dict={"method":method, "params": params, "new_res": new_res},body=
                {"auth":auth.model_dump(), "new_auth": new_auth},
                level=log_en.ERROR))
            raise ExceptionCallError(error=new_res["error"])

        return new_res
    except ExceptionCallError as error:
        raise error
    except ExceptionRefreshAuth as error:
        raise error
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application.", 
                   heder_dict=error.args,body=
                   {"auth":auth.model_dump(),"method":method, "params": params},
                    level=log_en.ERROR))
        raise ExceptionCallError(error="undefined")


async def refresh_auth(auth: AuthDTO, session: AsyncSession) -> Any:
    """
    Осуществляет обновление токена авторизации.
    Возврящяет следующую информацию:
    {
        "access_token": "XXXXXXXXX",
        "expires": 1722038365,
        "expires_in": 3600,
        "scope": "app",
        "domain": "oauth.bitrix.info",
        "server_endpoint": "https://oauth.bitrix.info/rest/",
        "status": "F",
        "client_endpoint": "https://b24-gqysfsnk1.bitrix24.ru/rest/",
        "member_id": "XXXXXXXXX",
        "user_id": 1,
        "refresh_token": "XXXXXXXXX"
    }
    """

    url = f"https://oauth.bitrix.info/oauth/token/?client_id={settings.C_REST_CLIENT_ID}&grant_type=refresh_token&client_secret={settings.C_REST_CLIENT_SECRET}&refresh_token={auth.refresh_token}"

    try:
        res = await send_http_post_request(url,None)

        if "error" in res:
            log(LogMessage(time=None,heder="Ошибка при выполнении refresh_auth.", 
                        heder_dict={"res":res},body=
                        {"auth":auth.model_dump()},
                        level=log_en.ERROR))
            raise ExceptionCallError(error=res["error"])

        await update_auth(session, res["member_id"], res["access_token"], res["expires_in"], res["client_endpoint"], res["refresh_token"])

        return res
    
    except ExceptionCallError as error:
        raise error
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при обновлении аутентификации.", 
                   heder_dict=error.args,body=
                   {"auth":auth.model_dump()},
                    level=log_en.ERROR))
        raise ExceptionRefreshAuth()


async def call_batch_web_hook(calls:list, halt: bool = False) -> Any:
    """
    Осуществляет выполнение пакета запросов.
    Calls:
    [
        {
            "method": "crm.contact.add",
            "params": {
                "FIELDS":{
                    "NAME":"Иван",
                    "LAST_NAME":"Петров"
                }
            }
        },
        ...
    ]
    """
    url=f"{settings.C_REST_WEB_HOOK_URL}/batch.json"+"?"+call_parameters_encoder_bath(calls)+f"&halt={'1' if halt else '0'}"

    try:
        res = await send_http_post_request(url,None)
        # добавить логику работы с огрничениями (очередь)

        if "error" in res:
            log(LogMessage(time=None,heder="Ошибка при выполнении call_batch_web_hook.", 
                        heder_dict={"res":res, "calls":calls, "halt": halt},body=
                        {},
                        level=log_en.ERROR))
            raise ExceptionCallError(error=res["error"])

        return res
    
    except ExceptionCallError as error:
        raise error
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении call_batch_web_hook.", 
                   heder_dict=error.args,body=
                   {"calls":calls, "halt": halt},
                    level=log_en.ERROR))
        raise ExceptionCallError(error="undefined")


async def call_batch_сirculation_application(auth: AuthDTO, calls:list, session: AsyncSession, halt: bool = False) -> Any:
    """
    Осуществляет выполнение пакета запросов.
    Calls:
    [
        {
            "method": "crm.contact.add",
            "params": {
                "FIELDS":{
                    "NAME":"Иван",
                    "LAST_NAME":"Петров"
                }
            }
        },
        ...
    ]
    """
    url=f"{auth.client_endpoint}/batch.json"+f"?auth={auth.access_token}&"+call_parameters_encoder_bath(calls)+f"&halt={'1' if halt else '0'}"

    try:
        res = await send_http_post_request(url,None)
        # добавить логику работы с огрничениями (очередь)

        if "error" in res:
            match res["error"]:
                case "expired_token":
                    recall_batch_сirculation_application(auth, calls, session, halt)
                case _:
                    log(LogMessage(time=None,heder="Ошибка при выполнении call_batch_сirculation_application.", 
                        heder_dict={"res":res, "calls":calls, "halt": halt},body=
                        {"auth":auth.model_dump()},
                        level=log_en.ERROR))
                    raise ExceptionCallError(error=res["error"])

        return res
    
    except ExceptionCallError as error:
        raise error
    except HTTPStatusError as error: # может возникнуть если пользователь сменил домен
        if error.response.status_code == 403:
            recall_batch_сirculation_application(auth, calls, session, halt)# повторная аутентификация полчит новый адресс
        else:
            raise ExceptionCallError(error="not_found")
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении call_batch_сirculation_application.", 
                   heder_dict=error.args,body=
                   {"calls":calls, "halt": halt},
                    level=log_en.ERROR))
        raise ExceptionCallError(error="undefined")
    

async def recall_batch_сirculation_application(auth: AuthDTO, calls:list, session: AsyncSession, halt: bool = False) -> Any:
    """
    Перевызов функции с повторной аутентификацией.
    """
    try:
        new_auth = await refresh_auth(auth, session)

        new_url=f"{auth.client_endpoint}/batch.json"+f"?auth={new_auth["access_token"]}&"+call_parameters_encoder_bath(calls)+f"&halt={'1' if halt else '0'}"

        new_res =  await send_http_post_request(new_url,None)
        # добавить логику работы с огрничениями (очередь)

        if "error" in new_res:
            log(LogMessage(time=None,heder="Ошибка при выполнении recall_batch_сirculation_application.", 
                heder_dict={"calls":calls, "halt": halt, "new_res": new_res},body=
                {"auth":auth.model_dump(), "new_auth": new_auth},
                level=log_en.ERROR))
            raise ExceptionCallError(error=new_res["error"])

        return new_res
    except ExceptionCallError as error:
        raise error
    except ExceptionRefreshAuth as error:
        raise error
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении recall_batch_сirculation_application.", 
                   heder_dict=error.args,body=
                   {"auth":auth.model_dump(),"calls":calls, "halt": halt},
                    level=log_en.ERROR))
        raise ExceptionCallError(error="undefined")