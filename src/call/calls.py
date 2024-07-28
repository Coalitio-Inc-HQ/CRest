from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder,call_parameters_encoder_batсh
from ..utils import send_http_post_request
from src.database.schemes import AuthDTO
from src.database.database_requests import update_auth, AsyncSession
from src.settings import settings

from httpx import HTTPStatusError

from src.loging.logging_utility import log, LogMessage,log_en

from typing import Any

import functools
import inspect


class ExceptionRefreshAuth(Exception):
    error: str

class ExceptionAuth(Exception):
    pass

class ExceptionKargAuthNotFound(Exception):
    pass

class ExceptionCallError(Exception):
    error: str

class ExceptionBatchCallError(Exception):
    pass

def error_catcher(name: str):
    """
    Параметр name исползуется для формирования названия ошибки: <Ошибка при выполнении декоратора {name}.>

    Выполняет обработку ошибок вызовов.
    В случае присудствия поля error в ответе вызывает исключение ExceptionCallError(error=<название ошибки>).
    """
    # QUERY_LIMIT_EXCEEDED подумать как реализовать
    """
    Расшифровка ошибок при выполени запроса b24:
    'expired_token' => 'истек токен, не могу получить новую аутентификацию? Проверьте доступ к серверу oauth.',
    'invalid_token' => 'недействительный токен, нужно переустановить приложение',
    'invalid_grant' => 'недействительный грант, проверьте определение C_REST_CLIENT_SECRET или C_REST_CLIENT_ID',
    'invalid_client' => 'недействительный клиент, проверьте определение C_REST_CLIENT_SECRET или C_REST_CLIENT_ID',
    'QUERY_LIMIT_EXCEEDED' => 'Слишком много запросов, максимум 2 запроса в секунду',
    'ERROR_METHOD_NOT_FOUND' => 'Метод не найден! Вы можете увидеть разрешения приложения: CRest::call(\'scope\')',
    'NO_AUTH_FOUND' => 'Ошибка настройки b24, проверьте в таблице "b_module_to_module" событие "OnRestCheckAuth"',
    'INTERNAL_SERVER_ERROR' => 'Сервер не работает, попробуйте позже'

    Собственные:
    'not_found' => 'Адресс b24 не найден.'
    'undefined' => 'Неизвестная ошибка.'
    """
    def wrapper(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                if "error" in result:
                    log(
                        LogMessage(
                            time=None,
                            heder=f"Ошибка при выполнении декоратора error_catcher, name: {name}.", 
                            heder_dict={"args":args, "kwargs":kwargs},
                            body={"result":result},
                            level=log_en.ERROR
                            )
                        )
                    raise ExceptionCallError(error=result["error"])

                return result
            
            except ExceptionCallError as error:
                raise error
            except ExceptionBatchCallError as error:
                raise error
            except ExceptionKargAuthNotFound as error:
                raise error
            except ExceptionAuth as error:
                raise error
            except ExceptionRefreshAuth as error:
                raise error
            except Exception as error:
                log(LogMessage(
                        time=None,
                        heder=f"Ошибка при выполнении декоратора error_catcher, name: {name}.", 
                        heder_dict={"args":args, "kwargs":kwargs},
                        body={"error_args":error.args},
                        level=log_en.ERROR
                        )
                    )
                raise ExceptionCallError(error="undefined")

        return inner
    return wrapper


def auto_refresh_token():
    """
    Используется для автоматического обновления токена, 
    а также в случае ошибки 403 (иожет возникнуть при смене домена) 
    позволет пройти повторную аутентификацию и получить новый домен.

    В случае ошибки аутентификации вызывает исключение ExceptionAuth().

    Для корректной работы обновления токена, необходимо передовать токен в параметр auth типа AuthDTO и session типа AsyncSession.

    В случае его отсудствия в kwargs будет вызвано исключение ExceptionKargAuthNotFound().
    """
    def wrapper(func):
        args_oder = inspect.signature(func).parameters.keys()
        index_auth = list(args_oder).index("auth")
        index_session = list(args_oder).index("session")


        async def recall(*args, **kwargs):
            session = None
            if "session" in kwargs and type(kwargs["session"])==AsyncSession:
                session = kwargs["session"]
            else:
                session = args[index_auth]

            auth = None
            if "auth" in kwargs and type(kwargs["auth"])==AuthDTO:
                auth = kwargs["auth"]
            else:
                auth = args[index_auth]

            try:
                new_auth = await refresh_auth(auth, session)

                auth.access_token = new_auth["access_token"]
                auth.expires_in = new_auth["expires_in"]
                auth.refresh_token = new_auth["refresh_token"]
                auth.client_endpoint = new_auth["client_endpoint"]

                try:
                    result = await func(*args, **kwargs)
                except HTTPStatusError as error: # может возникнуть если пользователь сменил домен
                    if error.response.status_code == 403:
                        log(LogMessage(
                            time=None,
                            heder=f"Ошибка при выполнении декоратора auto_refresh_token, recall, получен код 403.", 
                            heder_dict={"args":args, "kwargs":kwargs},
                            body={},
                            level=log_en.ERROR
                            )
                        )
                        raise ExceptionAuth()
                    else:
                        raise error

                if "error" in result:
                    if result["error"] =="expired_token":
                        log(LogMessage(
                            time=None,
                            heder=f"Ошибка при выполнении декоратора auto_refresh_token, recall, получена ошибка expired_token.", 
                            heder_dict={"args":args, "kwargs":kwargs},
                            body={},
                            level=log_en.ERROR
                            )
                        )
                        raise ExceptionAuth()

                return result

            except ExceptionRefreshAuth as error:
                raise ExceptionAuth()
            

        @functools.wraps(func)
        async def inner(*args, **kwargs):
            if (not "auth" in kwargs or type(kwargs["auth"])!=AuthDTO) and (len(args)<=index_auth or type(args[index_auth])!=AuthDTO):
                log(LogMessage(
                        time=None,
                        heder=f"Ошибка при выполнении декоратора auto_refresh_token, auth не найден или не яввляется объектом AuthDTO.", 
                        heder_dict={"args":args, "kwargs":kwargs},
                        body={},
                        level=log_en.ERROR
                        )
                    )
                raise ExceptionKargAuthNotFound()
            if (not "session" in kwargs or type(kwargs["session"])!=AsyncSession) and (len(args)<=index_session or type(args[index_session])!=AsyncSession):
                log(LogMessage(
                        time=None,
                        heder=f"Ошибка при выполнении декоратора auto_refresh_token, session не найден или не яввляется объектом AsyncSession.", 
                        heder_dict={"args":args, "kwargs":kwargs},
                        body={},
                        level=log_en.ERROR
                        )
                    )
                raise ExceptionKargAuthNotFound()


            try:
                result = await func(*args, **kwargs)
            except HTTPStatusError as error: # может возникнуть если пользователь сменил домен
                if error.response.status_code == 403:
                    return await recall(*args, **kwargs)
                else:
                    raise error


            if "error" in result:
                if result["error"] =="expired_token":
                    return await recall(*args, **kwargs)

            return result

        return inner
    return wrapper

@error_catcher("call_url_web_hook")
async def call_url_web_hook(method:str, params:dict) -> Any:
    """
    Осуществляет выполнение запроса через web hook.
    """

    url=f"{settings.C_REST_WEB_HOOK_URL}/{method}.json"+"?"+call_parameters_encoder(params)

    res = await send_http_post_request(url,None)
    # добавить логику работы с огрничениями (очередь)

    return res

@error_catcher("call_url_сirculation_application")
@auto_refresh_token()
async def call_url_сirculation_application(method:str, params:dict, auth: AuthDTO, session: AsyncSession) -> Any:
    """
    Осуществляет выполнение запроса через app.
    """
    params_temp = params
    params_temp["auth"] = auth.access_token

    url=f"{auth.client_endpoint}{method}.json"+"?"+call_parameters_encoder(params_temp)
    
    res = await send_http_post_request(url,None)
    # добавить логику работы с огрничениями (очередь)

    return res


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

    В случае ошибки аутентификации вызывается исключение ExceptionRefreshAuth(error)
    error:
    'expired_token' => 'истек токен, не могу получить новую аутентификацию? Проверьте доступ к серверу oauth.',
    'invalid_token' => 'недействительный токен, нужно переустановить приложение',
    'invalid_grant' => 'недействительный грант, проверьте определение C_REST_CLIENT_SECRET или C_REST_CLIENT_ID',
    'invalid_client' => 'недействительный клиент, проверьте определение C_REST_CLIENT_SECRET или C_REST_CLIENT_ID',
    'QUERY_LIMIT_EXCEEDED' => 'Слишком много запросов, максимум 2 запроса в секунду',
    'ERROR_METHOD_NOT_FOUND' => 'Метод не найден! Вы можете увидеть разрешения приложения: CRest::call(\'scope\')',
    'NO_AUTH_FOUND' => 'Ошибка настройки b24, проверьте в таблице "b_module_to_module" событие "OnRestCheckAuth"',
    'INTERNAL_SERVER_ERROR' => 'Сервер не работает, попробуйте позже'

    'undefined' => 'Неизвестная ошибка.'
    """

    url = f"https://oauth.bitrix.info/oauth/token/?client_id={settings.C_REST_CLIENT_ID}&grant_type=refresh_token&client_secret={settings.C_REST_CLIENT_SECRET}&refresh_token={auth.refresh_token}"

    try:
        result = await send_http_post_request(url,None)

        if "error" in result:
            log(LogMessage(
                time=None,
                heder="Ошибка при выполнении refresh_auth.", 
                heder_dict={"auth":auth},
                body={"result":result},
                level=log_en.ERROR))
            raise ExceptionRefreshAuth(error=result["error"])

        await update_auth(session, result["member_id"], result["access_token"], result["expires_in"], result["client_endpoint"], result["refresh_token"])

        return result
    
    except ExceptionRefreshAuth as error:
        raise error
    except Exception as error:
        log(LogMessage(
                time=None,
                heder="Ошибка при выполнении refresh_auth.", 
                heder_dict={"auth":auth},
                body={"result":result},
                level=log_en.ERROR))
        raise ExceptionRefreshAuth(error="undefined")

@error_catcher("call_batch_web_hook")
async def call_batch_web_hook(calls:list, halt: bool = False) -> list:
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

    !!! Примечание кодирование массива начинается с 1 т.к. в таком случае в ответе содержатся индексы.
    !!! Также если, происходит ошибка в первом методе, то он не нумеруется.
    !!! По этому нумерация с 1.
    """

    params = call_parameters_encoder_batсh(calls)

    res = []

    for param in params:
        try:
            temp_res = await sub_call_batch_web_hook(param, halt)
            res.append(temp_res)
            if halt and "result" in temp_res and "result_error" in temp_res["result"] and temp_res["result"]["result_error"] != []:
                break
        except:
            if halt:
                break

    # добавить логику работы с огрничениями (очередь)

    if len(res) == 0:
        raise ExceptionBatchCallError()

    return res
    
@error_catcher("sub_call_batch_web_hook")
async def sub_call_batch_web_hook(param: str, halt: bool = False) -> Any:
    """
    Вызывает сигмент batch по web_hook.
    """
    url=f"{settings.C_REST_WEB_HOOK_URL}/batch.json"+"?"+param+f"&halt={'1' if halt else '0'}"
    return await send_http_post_request(url,None)


@error_catcher("call_batch_сirculation_application")
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
    params = call_parameters_encoder_batсh(calls)

    res = []

    for param in params:
        try:
            temp_res = await sub_call_batch_сirculation_application(auth, param, session, halt)
            res.append(temp_res)
            if halt and "result" in temp_res and "result_error" in temp_res["result"] and temp_res["result"]["result_error"] != []:
                break
        except:
            if halt:
                break

    # добавить логику работы с огрничениями (очередь)

    if len(res) == 0:
        raise ExceptionBatchCallError()

    return res

@error_catcher("sub_call_batch_сirculation_application")
@auto_refresh_token()
async def sub_call_batch_сirculation_application(auth: AuthDTO, param: str, session: AsyncSession, halt: bool = False) -> Any:
    """
    Вызывает сигмент batch по сirculation_application.
    """
    url=f"{auth.client_endpoint}/batch.json"+f"?auth={auth.access_token}&"+param+f"&halt={'1' if halt else '0'}"
    return await send_http_post_request(url,None)
