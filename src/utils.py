from httpx import AsyncClient, HTTPStatusError
from typing import Any
from src.loging.logging_utility import log, LogMessage,log_en

from urllib.parse import unquote_plus
import json

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
        

def decode_auth(encoded_string:str) -> dict:
    """
    Осуществляет декодирование строки аутентификации.
    """
    string = encoded_string[2:-1]

    parsed_components = {}
    for component in string.split('&'):
        key, value = component.split('=')
        if key!="PLACEMENT_OPTIONS":
            parsed_components[key] = value
        else:
            parsed_components[key] = json.loads(unquote_plus(value))
    return parsed_components