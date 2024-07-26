from .settings import get_app_settings, get_url
from .call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder
from .utils import send_http_post_request

from typing import Any

async def call_url(method:str, params:dict) -> Any:
    """
    Осуществляет выполнение запроса.
    """

    url=get_url(method)+"?"+call_parameters_encoder(params)

    try:
        res = await send_http_post_request(url,None)
        # добавить логику раьоты с огрничениями (очередь)
        return res
    except:
        pass

# async def call_batch_url(calls:list) -> Any:
#     """
#     Осуществляет выполнение пакета запросов.
#     """
    

