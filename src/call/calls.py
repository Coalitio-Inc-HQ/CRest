from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder,call_parameters_encoder_batсh
from src.settings import settings

from .url_bilders.url_builder import UrlBuilder

from httpx import HTTPStatusError

from src.loging.logging_utility import log, LogMessage,log_en, filter_array_to_str, filter_dict_to_str

from .call_director import barrel_strategy_call_director

from typing import Any

from .call_execute import ExceptionRefreshAuth

from .call_director import ExceptionCallError

import functools
import inspect

import math
"""
TODO
Пулы.
"""


class ExceptionAuth(Exception):
    pass


class ExceptionKargAuthNotFound(Exception):
    pass


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


@error_catcher("call_method")
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
    res = await barrel_strategy_call_director.call_request(url_builder, method, params)

    return res


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
    return await barrel_strategy_call_director.call_bath_request(url_builder,calls,halt)
    

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
    
