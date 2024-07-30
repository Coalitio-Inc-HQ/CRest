from httpx import AsyncClient, HTTPStatusError
from typing import Any
from src.loging.logging_utility import log, LogMessage,log_en

from src.call.url_builder import UrlBuilder

from urllib.parse import unquote_plus
import json


async def send_http_post_request_url_builder(url_builder: UrlBuilder, method:str,param: str) -> Any:
    """
    Отправляет post запрос.
    Учитывет редикт.
    """
    async with AsyncClient(timeout=10.0) as clinet:
        try:
            response = await clinet.post(url_builder.build_url(method, param))
            if response.status_code == 302:
                await url_builder.update_domain(response.headers['Location'])
                response = await clinet.post(url_builder.build_url(method, param))
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as error:
            log(LogMessage(time=None,
                    heder=f"Ошибка выполнения запроса. {error.response.status_code}", 
                    heder_dict=error.args,
                    body={
                        "url":url_builder.build_url(method, param), 
                        "method":method,
                        "param": param,
                        "response":error.response.json()
                    },
                    level=log_en.ERROR))
            raise error
        except Exception as error:
            log(LogMessage(time=None,
                            heder="Неизвестная ошибка.", 
                            heder_dict=error.args,
                            body={
                                "url":url_builder.build_url(method, param), 
                                "method":method,
                                "param": param
                            },
                            level=log_en.ERROR))
            raise error


async def send_http_post_request(url:str, json: Any|None) -> Any:
    """
    Отправляет post запрос.
    """
    async with AsyncClient() as clinet:
        try:
            response = await clinet.post(url, json=json)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as error:
            log(LogMessage(time=None,heder=f"Ошибка выполнения запроса. {error.response.status_code}", 
                   heder_dict=error.args,body=
                    {
                        "url":url, 
                        "json":json,
                        "response":error.response.json()
                    },
                    level=log_en.ERROR))
            raise error
        except Exception as error:
            log(LogMessage(time=None,heder="Неизвестная ошибка.", 
                   heder_dict=error.args,body=
                    {
                        "url":url, 
                        "json":json
                    },
                    level=log_en.ERROR))
            raise error