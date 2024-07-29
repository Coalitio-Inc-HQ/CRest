from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder,call_parameters_encoder_batсh
from ..utils import send_http_post_request, send_http_post_request_url_builder
from src.database.schemes import AuthDTO
from src.database.database_requests import update_auth, AsyncSession
from src.settings import settings

from .url_builder import UrlBuilder

from httpx import HTTPStatusError

from src.loging.logging_utility import log, LogMessage,log_en, filter_array_to_str, filter_dict_to_str

from typing import Any

import functools
import inspect

import math
"""
TODO
Ввести ограничение времени запроса.
https://dev.1c-bitrix.ru/rest_help/rest_sum/index.php.

Пулы.
"""


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
                            heder_dict={"args": filter_array_to_str(args), "kwargs": filter_dict_to_str(kwargs)},
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
                        heder_dict={"args": filter_array_to_str(args), "kwargs": filter_dict_to_str(kwargs)},
                        body={"error_args":error.args},
                        level=log_en.ERROR
                        )
                    )
                raise ExceptionCallError(error="undefined")

        return inner
    return wrapper


def auto_refresh_token():
    """
    Используется для автоматического обновления токена.

    В случае ошибки аутентификации вызывает исключение ExceptionAuth().

    Для корректной работы обновления токена, необходимо передовать url_builder: UrlBuilder.

    В случае его отсудствия в kwargs будет вызвано исключение ExceptionKargAuthNotFound().
    """
    def wrapper(func):
        args_oder = inspect.signature(func).parameters.keys()
        index_url_builder = list(args_oder).index("url_builder")


        async def recall(*args, **kwargs):
            url_builder = None
            if "url_builder" in kwargs and type(kwargs["url_builder"])==UrlBuilder:
                url_builder = kwargs["url_builder"]
            else:
                url_builder = args[index_url_builder]


            try:
                await refresh_auth(url_builder)

                try:
                    result = await func(*args, **kwargs)
                except HTTPStatusError as error: # может возникнуть если пользователь сменил домен
                    if error.response.status_code == 401:
                        log(LogMessage(
                            time=None,
                            heder=f"Ошибка при выполнении декоратора auto_refresh_token, recall, получен код 401.", 
                            heder_dict={"args": filter_array_to_str(args), "kwargs": filter_dict_to_str(kwargs)},
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
                            heder_dict={"args": filter_array_to_str(args), "kwargs": filter_dict_to_str(kwargs)},
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
            if (not "url_builder" in kwargs or not issubclass(type(kwargs["url_builder"]), UrlBuilder)) and (len(args)<=index_url_builder or not issubclass(type(args[index_url_builder]),UrlBuilder)):
                log(LogMessage(
                        time=None,
                        heder=f"Ошибка при выполнении декоратора auto_refresh_token, url_builder не найден или не яввляется объектом UrlBuilder.", 
                        heder_dict={"args": filter_array_to_str(args), "kwargs": filter_dict_to_str(kwargs)},
                        body={},
                        level=log_en.ERROR
                        )
                    )
                raise ExceptionKargAuthNotFound()
            

            try:
                result = await func(*args, **kwargs)
            except HTTPStatusError as error: 
                if error.response.status_code == 401:
                    url_builder = None
                    if "url_builder" in kwargs and type(kwargs["url_builder"])==UrlBuilder:
                        url_builder = kwargs["url_builder"]
                    else:
                        url_builder = args[index_url_builder]

                    if url_builder.is_reauth:
                        return await recall(*args, **kwargs)
                    else:
                        raise ExceptionAuth()
                else:
                    raise error


            if "error" in result:
                if result["error"] =="expired_token":

                    url_builder = None
                    if "url_builder" in kwargs and type(kwargs["url_builder"])==UrlBuilder:
                        url_builder = kwargs["url_builder"]
                    else:
                        url_builder = args[index_url_builder]

                    if url_builder.is_reauth:
                        return await recall(*args, **kwargs)
                    else: 
                        raise ExceptionAuth()

            return result

        return inner
    return wrapper


@error_catcher("call_method")
@auto_refresh_token()
async def call_method(url_builder: UrlBuilder, method:str, params:dict) -> Any:
    """
    Осуществляет выполнение запроса через.
    Пример:
    url_builder - сборщик url
    method = "crm.contact.add"
    params = {
        "FIELDS":{
            "NAME":"Иван1",
            "LAST_NAME":"Петров1"
        }
    }
    """
    res = await send_http_post_request_url_builder(url_builder, method, call_parameters_encoder(params))
    # добавить логику работы с огрничениями (очередь)

    return res


async def refresh_auth(url_builder: UrlBuilder) -> Any:
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
    try:
        result = await send_http_post_request(url_builder.build_url_update_auth(),None)

        if "error" in result:
            log(LogMessage(
                time=None,
                heder="Ошибка при выполнении refresh_auth.", 
                heder_dict={"auth_url": url_builder.build_url_update_auth()},
                body={"result":result},
                level=log_en.ERROR))
            raise ExceptionRefreshAuth(error=result["error"])
        
        await url_builder.update_auth(result["access_token"], int(result["expires_in"]), result["client_endpoint"], result["refresh_token"])

        return result
    
    except ExceptionRefreshAuth as error:
        raise error
    except Exception as error:
        log(LogMessage(
                time=None,
                heder="Ошибка при выполнении refresh_auth.", 
                heder_dict={"auth_url": url_builder.build_url_update_auth()},
                body={},
                level=log_en.ERROR))
        raise ExceptionRefreshAuth(error="undefined")


@error_catcher("call_batch")
async def call_batch(url_builder: UrlBuilder, calls:list, halt: bool = False) -> list:
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
    halt указывает прерывать ли выполнение запроса при возниконовени ошибки в одном из методов. RollBack не происходит.

    !!! Примечание кодирование массива начинается с 1 т.к. в таком случае в ответе содержатся индексы.
    !!! Также если, происходит ошибка в первом методе, то он не нумеруется.
    !!! По этому нумерация с 1.
    """

    params = call_parameters_encoder_batсh(calls)

    res = []

    for param in params:
        try:
            temp_res = await sub_call_batch(url_builder, param, halt)
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
    

@error_catcher("sub_call_batch")
@auto_refresh_token()
async def sub_call_batch(url_builder: UrlBuilder, param: str, halt: bool = False) -> Any:
    """
    Вызывает сигмент batch.
    """
    return await send_http_post_request_url_builder(url_builder,"batch",param+f"&halt={'1' if halt else '0'}")


async def get_list(url_builder: UrlBuilder, method:str, params:dict | None = None) -> list:
    """
    Выполняет извлечение списка с помощью метода method и параметров params.
    Возвращяет весь список сразу.

    Автоматически сортерует значения по ID ASC.
    В случае указания DESC также работает.
    Параметр start устанавливается в -1.
    """
    is_id_oder_normal = True
    if params:
        if "order" in params:
            if "ID" in params["order"]:
                if params["order"]["ID"] == "DESC":
                    is_id_oder_normal = False
            else:
                params["order"]["ID"] = "ASC"
        else:
            params["order"] = {
                "ID":"ASC"
            }
    else:
        params = {
            "order":{
                "ID":"ASC"
            }
        }

    params["start"] = "-1"

    last_id = None

    result = []

    while True:
        params_coppy = params.copy()
        if last_id:
            if "filter" in params:
                params_coppy["filter"][f"{">" if is_id_oder_normal else "<"}ID"] = str(last_id)

            else:
                params_coppy["filter"] = {f"{">" if is_id_oder_normal else "<"}ID": str(last_id)}

        res = await call_method(url_builder, method, params_coppy)

        if len(res["result"]) == 0:
            break
        
        last_id = int(res["result"][len(res["result"])-1]["ID"])

        result.extend(res["result"])
    
    return result


async def get_list_bath(url_builder: UrlBuilder, method:str, params:dict | None = None) -> list:
    """
    Выполняет извлечение списка с помощью метода method и параметров params.
    Возвращяет весь список сразу.
    """
    if not params:
        params = {}

    result = []

    res = await call_method(url_builder, method, params)

    result.extend(res["result"])

    total = int(res["total"])

    count = math.ceil(total/settings.RETURN_LIST_COUNT)-1

    bath_params = []
    for i in range(count):
        copy_params = params.copy()
        copy_params["start"] = str(settings.RETURN_LIST_COUNT*(i+1))
        bath_params.append(
            {
                "method": method,
                "params":copy_params
            }
        )
    
    bath_res = await call_batch(url_builder, bath_params)

    for bath_item in bath_res:
        for key, item in bath_item["result"]["result"].items():
            result.extend(item)
    return result


async def get_list_generator(url_builder: UrlBuilder, method:str, params:dict | None = None):
    """
    Выполняет извлечение списка с помощью метода method и параметров params.

    Автоматически сортерует значения по ID ASC.
    В случае указания DESC также работает.
    Параметр start устанавливается в -1.
    """
    is_id_oder_normal = True
    if params:
        if "order" in params:
            if "ID" in params["order"]:
                if params["order"]["ID"] == "DESC":
                    is_id_oder_normal = False
            else:
                params["order"]["ID"] = "ASC"
        else:
            params["order"] = {
                "ID":"ASC"
            }
    else:
        params = {
            "order":{
                "ID":"ASC"
            }
        }

    params["start"] = "-1"

    last_id = None


    while True:
        params_coppy = params.copy()
        if last_id:
            if "filter" in params:
                params_coppy["filter"][f"{">" if is_id_oder_normal else "<"}ID"] = str(last_id)

            else:
                params_coppy["filter"] = {f"{">" if is_id_oder_normal else "<"}ID": str(last_id)}

        res = await call_method(url_builder, method, params_coppy)

        if len(res["result"]) == 0:
            break
        
        last_id = int(res["result"][len(res["result"])-1]["ID"])

        for item in res["result"]:
            yield item
    
