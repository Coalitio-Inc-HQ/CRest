from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder
from ..utils import send_http_post_request
from src.database.schemes import AuthDTO
from src.database.database_requests import update_auth, AsyncSession
from src.settings import settings

from src.loging.logging_utility import log, LogMessage,log_en

from typing import Any

class ExceptionRefreshAuth(Exception):
    pass

class ExceptionCallError(Exception):
    pass

async def call_url_web_hook(method:str, params:dict) -> Any:
    """
    Осуществляет выполнение запроса через web hook.
    """

    url=f"{settings.C_REST_WEB_HOOK_URL}/{method}.json"+"?"+call_parameters_encoder(params)

    try:
        res = await send_http_post_request(url,None)
        # добавить логику работы с огрничениями (очередь)

        if "error" in res:
            log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application.", 
                        heder_dict={"res":res, "method":method, "params": params},body=
                        {},
                        level=log_en.ERROR))
            raise ExceptionCallError()

        return res
    except:
        pass


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
                    new_auth = await refresh_auth(auth, session)

                    params_temp = params
                    params_temp["auth"] = new_auth["access_token"]

                    new_url=f"{new_auth["client_endpoint"]}{method}.json"+"?"+call_parameters_encoder(params_temp)
                    # добавить логику работы с огрничениями (очередь)

                    new_res =  await send_http_post_request(new_url,None)

                    if "error" in new_res:
                        log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application в блоке new_auth.", 
                            heder_dict={"res":res, "method":method, "params": params, "new_res": new_res},body=
                            {"auth":auth.model_dump(), "new_auth": new_auth},
                            level=log_en.ERROR))
                        raise ExceptionCallError()

                    return new_res
                    
                case _:
                    log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application.", 
                        heder_dict={"res":res, "method":method, "params": params},body=
                        {"auth":auth.model_dump()},
                        level=log_en.ERROR))
                    raise ExceptionCallError()


        return res
    except Exception as error:
        log(LogMessage(time=None,heder="Ошибка при выполнении call_url_сirculation_application.", 
                   heder_dict=error.args,body=
                   {"auth":auth.model_dump(),"method":method, "params": params},
                    level=log_en.ERROR))
        raise error
        # raise ExceptionRefreshAuth()


async def refresh_auth(auth: AuthDTO, session: AsyncSession) -> str:
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
            raise ExceptionCallError()

        await update_auth(session, res["member_id"], res["access_token"], res["expires_in"], res["client_endpoint"], res["refresh_token"])

        return res
    
    except Exception as error:

        log(LogMessage(time=None,heder="Ошибка при обновлении аутентификации.", 
                   heder_dict=error.args,body=
                   {"auth":auth.model_dump()},
                    level=log_en.ERROR))
        raise ExceptionRefreshAuth()


# async def call_batch_url(calls:list) -> Any:
#     """
#     Осуществляет выполнение пакета запросов.
#     """
    

