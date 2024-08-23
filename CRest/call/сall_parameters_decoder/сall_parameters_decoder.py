from fastapi import Request
import re
from urllib.parse import unquote

def call_parameters_decoder(string: str) -> dict:
    arr = string.split("&")

    res = {}

    for param in arr:
        key, value = param.split('=')
        key = unquote(key)
        value = unquote(value)
        keys = list(filter(bool, re.split("[\[\]]",key)))

        last_dict = res

        for i in range(len(keys)):
            if (i+1==len(keys)):
                last_dict[keys[i]] = value
            else:
                if keys[i] in last_dict:
                    last_dict = last_dict[keys[i]]
                else:
                    new = {}
                    last_dict[keys[i]] = new
                    last_dict = new

    return res


async def decode_body_request(request: Request) -> dict | None:
    # Извлечение тела запроса
    content_type = request.headers.get("content-type")
    body = None
    if content_type == "application/json":
        body = await request.json()
    elif content_type == "application/x-www-form-urlencoded":
        body = await decode_body_request(request)
    request.state.body = body

    return body

# def get_body(request: Request) -> dict | None:
#     if request.state.body:
#         return request.state.body
#     else:
#         return None