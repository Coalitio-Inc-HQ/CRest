from typing import Any
from src.call.url_builder import UrlBuilder
from src.utils import send_http_post_request_url_builder
import datetime
from src.settings import settings
import time
from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder,call_parameters_encoder_batсh

from httpx import HTTPStatusError

class CallDirector:
    """
    Ответственность:
    1) Соблюдение ограничений.
    2) Контроль 503 (следствие нарушения ограничений).
    3) Окончательная сборка запроса (Почему именно здесь? - Потому, что именно здесь можно осуществлять компоновку зпросов в batch).
    """
    async def call_request(self,url_builder: UrlBuilder, method:str, params:dict) -> Any:
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
        if url_builder.get_member_id() in self.domains_data:
            return self.domains_data[url_builder.get_member_id()]
        else:
            domain_info = {
                "number_of_requests": 0,
                "method_operating":{}
            }
            self.domains_data[url_builder.get_member_id()] = domain_info
            return domain_info

    # @staticmethod
    # def chek_method(domain_info: dict, method:str) -> bool:
    #     """
    #     Проверяет ограничения для доменной зоны.
    #     1 - достигнуто ограничение.
    #     """
    #     if not method in domain_info["method_operating"]:
    #         method_operating_info = {
    #             "sum_time": 0,
    #             "operating_reset_at": datetime.datetime.now()
    #         }
    #         domain_info["method_operating"][method]= method_operating_info
    #         return False
    #     else:
    #         method_operating_info = domain_info["method_operating"][method]

    #         if method_operating_info["operating_reset_at"]<datetime.datetime.now():
    #             return False
    #         elif method_operating_info["sum_time"]<settings.OPERATING_MAX_TIME:
    #             return False
    #         else:
    #             return True
    
    # @staticmethod
    # def update_method_info(domain_info: dict, method:str, operating: float, operating_reset_at: datetime.datetime):
    #     method_info = domain_info["method_operating"][method]

    #     if operating_reset_at != method_info["operating_reset_at"]:
    #         method_info["operating_reset_at"] = operating_reset_at
    #         method_info["sum_time"] = operating
    #     else:
    #         method_info["sum_time"]+= operating



    # async def call_request(self,url_builder: UrlBuilder, method:str, params:dict) -> Any:
    #     domain_info = self.get_domain_info(url_builder)

    #     while domain_info["number_of_requests"]>70 or self.chek_method(domain_info, method):
    #         time.sleep(0.5)
        
    #     domain_info["number_of_requests"]+=1

    #     res = await send_http_post_request_url_builder(url_builder,method, call_parameters_encoder(params))

    #     domain_info["number_of_requests"]-=1

    #     if "time" in res:
    #             self.update_method_info(domain_info, method, float(res["time"]["operating"]), datetime.datetime.fromtimestamp(res["time"]["operating_reset_at"]))

    #     return res


    # async def call_bath_request(self,url_builder: UrlBuilder, method:str,param: str) -> Any:
    #     pass
    
    async def call_request(self,url_builder: UrlBuilder, method:str, params:dict) -> Any:
        domain_info = self.get_domain_info(url_builder)

        while domain_info["number_of_requests"]>70:
            time.sleep(0.5)
        
        domain_info["number_of_requests"]+=1

        try:
            while True:
                try:
                    res = await send_http_post_request_url_builder(url_builder,method, call_parameters_encoder(params))

                    if "error" in res:
                        if res["error"] =="OPERATION_TIME_LIMIT":
                            raise self.Exception503()

                    break

                except self.Exception503 as error:
                    time.sleep(1)
                except HTTPStatusError as error: 
                        if error.response.status_code == 503:
                            time.sleep(1)
                        else:
                            raise error

                if "error" in res:
                        if res["error"] == "QUERY_LIMIT_EXCEEDED":
                            raise self.Exception503()
        finally:
            domain_info["number_of_requests"]-=1

        return res


    async def call_bath_request(self,url_builder: UrlBuilder, method:str,param: str) -> Any:
        domain_info = self.get_domain_info(url_builder)

        while domain_info["number_of_requests"]>70:
            time.sleep(0.5)
        
        domain_info["number_of_requests"]+=1

        try:
            while True:
                try:
                    res = await send_http_post_request_url_builder(url_builder,method, param)

                    if "result_error" in res["result"]:
                        if type(res["result"]["result_error"]) == dict:
                            for key, value in res["result"]["result_error"].items():
                                if "error" in value and value["error"] == "OPERATION_TIME_LIMIT":
                                    raise self.Exception503()

                    if "error" in res:
                        if res["error"] == "QUERY_LIMIT_EXCEEDED":
                            raise self.Exception503()

                    break
                except self.Exception503 as error:
                    print("Превышен operating")
                    time.sleep(1)

                except HTTPStatusError as error: 
                        if error.response.status_code == 503:
                            print("Превышен operating")
                            time.sleep(1)
                        else:
                            raise error

        finally:
            domain_info["number_of_requests"]-=1

        return res

    class Exception503(Exception):
        pass



barrel_strategy_call_director = CallDirectorBarrelStrategy()