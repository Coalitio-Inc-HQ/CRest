from typing import Any
from src.call.url_builders.url_builder import UrlBuilder
import datetime
from src.settings import settings
import time
from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder,call_parameters_encoder_batсh, call_parameters_encoder_batсh_by_index

import asyncio    

from .call_execute import call_execute

from httpx import HTTPStatusError

class ExceptionCallError(Exception):
    error: str

class CallDirector:
    """
    Ответственность:
    1) Соблюдение ограничений.
    2) Контроль 503 (следствие нарушения ограничений).
    3) Окончательная сборка запроса (Почему именно здесь? - Потому, что именно здесь можно осуществлять компоновку зпросов в batch).
    """
    async def call_request(self,url_builder: UrlBuilder, method:str, params:dict) -> Any:
        pass

    async def call_bath_request(self,url_builder: UrlBuilder,calls:list, halt: bool) -> Any:
        pass


class CallDirectorBarrelStrategy(CallDirector):
    """
    Простейший вариант управления запросаим.
    """

    """
    Не понятно как работает operating.

    В python один operating, в постмене другой, причём для одного и тоже запроса. => operating локален для конкретного сервара. (в python я добился ошибки 503, а в постмене всё работало.)

    "Поле operating_reset_at возвращает timestamp в которое будет высвобождена часть лимита на данный метод", но фактически это время вызова метода + 10 мин. и подождав 1 с. можно, практически гарантированно вызовать метод повторно (конкретно для crm.contact.add).

    "operating, который говорит о времени выполнения запроса к методу конкретным приложением", почему-то приходит сумма.

    Похоже единственный вариант это сделать список operating_reset_at для каждого метода и при возникновении 503 ждать ближайшего времени.
    """
    def __init__(self) -> None:
        self.domains_data = {}

    def get_domain_info(self, url_builder: UrlBuilder) -> dict:
        """
        Получает информацию о доменной зоне или создаёт её.
        """
        if url_builder.get_name() in self.domains_data:
            return self.domains_data[url_builder.get_name()]
        else:
            domain_info = {
                "number_of_requests": 0,
                "method_operating":{}
            }
            self.domains_data[url_builder.get_name()] = domain_info
            return domain_info

    
    async def call_request(self,url_builder: UrlBuilder, method:str, params:dict) -> Any:
        domain_info = self.get_domain_info(url_builder)

        while domain_info["number_of_requests"]>70:
            await asyncio.sleep(0.5)
        
        domain_info["number_of_requests"]+=1
        try:
            while True:
                try:
                    res = await call_execute(url_builder,method, call_parameters_encoder(params))

                    if "error" in res:
                        if res["error"] =="OPERATION_TIME_LIMIT":
                            raise self.Exception503()
                        elif res["error"] == "QUERY_LIMIT_EXCEEDED":
                            raise self.Exception503()
                    break

                except self.Exception503 as error:
                    await asyncio.sleep(1)
                except HTTPStatusError as error: 
                        if error.response.status_code == 503:
                            await asyncio.sleep(1)
                        else:
                            raise error
        finally:
            domain_info["number_of_requests"]-=1

        return res



    async def call_bath_request(self,url_builder: UrlBuilder,calls:list, halt: bool) -> Any:
        domain_info = self.get_domain_info(url_builder)

        while domain_info["number_of_requests"]>70:
            await asyncio.sleep(0.5)
        
        domain_info["number_of_requests"]+=1

        try:
            if halt:
                total_res = {
                    "result":{
                        "result":{

                        },
                        "result_error":{

                        },
                        "result_time":{

                        }
                    }
                }
                start_index = 0
                
                while start_index != len(calls):
                    end_index = start_index+settings.BATCH_COUNT if start_index+settings.BATCH_COUNT<= len(calls) else len(calls)
                    build_params = call_parameters_encoder_batсh(calls, start_index, end_index)+f"&halt=1"

                    try:
                        res = await call_execute(url_builder,"batch", build_params)

                        if "error" in res:
                            if res["error"] =="OPERATION_TIME_LIMIT":
                                raise self.Exception503()
                            elif res["error"] == "QUERY_LIMIT_EXCEEDED":
                                raise self.Exception503()
                            else:
                                break
                            
                        if (type(res["result"]["result"]) ==dict):
                            last_index = -1
                            for key, value in res["result"]["result"].items():
                                total_res["result"]["result"][key] = value
                                if int(key)>last_index:
                                    last_index = int(key)
                            start_index = last_index

                        if (type(res["result"]["result_time"]) ==dict):
                            for key, value in res["result"]["result_time"].items():
                                total_res["result"]["result_time"][key] = value


                        if "result_error" in res["result"]:
                            if type(res["result"]["result_error"]) == dict:
                                ex = False
                                for key, value in res["result"]["result_error"].items():
                                    if "error" in value and value["error"] == "OPERATION_TIME_LIMIT":
                                        raise self.Exception503()
                                    else:
                                        total_res["result"]["result_error"][key]=value
                                        ex = True
                                        break
                                if ex:
                                    break
                        

                    except self.Exception503 as error:
                        await asyncio.sleep(1)
                    except HTTPStatusError as error: 
                            if error.response.status_code == 503:
                                await asyncio.sleep(1)
                            else:
                                raise error
                return total_res


            else:
                total_res = {
                    "result":{
                        "result":{

                        },
                        "result_error":{

                        },
                        "result_time":{

                        }
                    }
                }
                start_index = 0
                
                fails = []

                while start_index != len(calls):
                    end_index = start_index+settings.BATCH_COUNT if start_index+settings.BATCH_COUNT<= len(calls) else len(calls)
                    build_params = call_parameters_encoder_batсh(calls, start_index, end_index)+f"&halt=0"

                    try:
                        res = await call_execute(url_builder,"batch", build_params)

                        if "error" in res:
                            if res["error"] =="OPERATION_TIME_LIMIT":
                                raise self.Exception503()
                            elif res["error"] == "QUERY_LIMIT_EXCEEDED":
                                raise self.Exception503()
                            else:
                                break
                        
                        last_index = -1
                        if (type(res["result"]["result"]) ==dict):
                            for key, value in res["result"]["result"].items():
                                total_res["result"]["result"][key] = value
                                if int(key)>last_index:
                                    last_index = int(key)
                        

                        if (type(res["result"]["result_time"]) ==dict):
                            for key, value in res["result"]["result_time"].items():
                                total_res["result"]["result_time"][key] = value


                        if "result_error" in res["result"]:
                            if type(res["result"]["result_error"]) == dict:
                                for key, value in res["result"]["result_error"].items():
                                    if "error" in value and value["error"] == "OPERATION_TIME_LIMIT":
                                        fails.append(int(key)-1)
                                    else:
                                        total_res["result"]["result_error"][key]=value
                                    last_index = int(key)
                        start_index = last_index
                                        
                        

                    except self.Exception503 as error:
                        await asyncio.sleep(1)
                    except HTTPStatusError as error: 
                            if error.response.status_code == 503:
                                await asyncio.sleep(1)
                            else:
                                raise error
                            
                while len(fails)!= 0:
                    build_params = call_parameters_encoder_batсh_by_index(calls, fails[0:settings.BATCH_COUNT])+f"&halt=0"

                    try:
                        res = await call_execute(url_builder,"batch", build_params)

                        if "error" in res:
                            if res["error"] =="OPERATION_TIME_LIMIT":
                                raise self.Exception503()
                            elif res["error"] == "QUERY_LIMIT_EXCEEDED":
                                raise self.Exception503()
                            else:
                                break
                        
                        if (type(res["result"]["result"]) ==dict):
                            for key, value in res["result"]["result"].items():
                                total_res["result"]["result"][key] = value
                                fails.remove(int(key)-1)

                        if (type(res["result"]["result_time"]) ==dict):
                            for key, value in res["result"]["result_time"].items():
                                total_res["result"]["result_time"][key] = value

                        if "result_error" in res["result"]:
                            if type(res["result"]["result_error"]) == dict:
                                for key, value in res["result"]["result_error"].items():
                                    if "error" in value and value["error"] == "OPERATION_TIME_LIMIT":
                                        pass
                                    else:
                                        total_res["result"]["result_error"][key]=value
                                        fails.remove(int(key)-1)
                                        
                        

                    except self.Exception503 as error:
                        await asyncio.sleep(1)
                    except HTTPStatusError as error: 
                            if error.response.status_code == 503:
                                await asyncio.sleep(1)
                            else:
                                raise error


                return total_res

        finally:
            domain_info["number_of_requests"]-=1

