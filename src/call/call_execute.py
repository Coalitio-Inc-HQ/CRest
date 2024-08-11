from httpx import AsyncClient, HTTPStatusError
from typing import Any
from src.loging.logging_utility import log, LogMessage, log_en

from src.call.url_bilders.url_builder import UrlBuilder
from src.call.url_bilders.url_builder import ExceptionRefreshAuth


async def call_execute(url_builder: UrlBuilder, method: str, param_str: str) -> Any:
    """
    Осуществляет выполнение запроса с учётом переадрисации и обновления токена.
    """
    async with AsyncClient(timeout=10.0) as clinet:
        try:
            response = await clinet.post(url_builder.build_url(method, param_str))

            if response.status_code == 401:
                if url_builder.is_reauth:
                    await url_builder.update_auth()
                    response = await clinet.post(url_builder.build_url(method, param_str))
            elif response.status_code == 302:
                await url_builder.update_domain(response.headers['Location'])
                response = await clinet.post(url_builder.build_url(method, param_str))

            response.raise_for_status()
            return response.json()

        except ExceptionRefreshAuth as error:
            raise error
        except HTTPStatusError as error:
            log(LogMessage(
                time=None,
                heder=f"Ошибка выполнения запроса. {
                    error.response.status_code}",
                heder_dict=error.args,
                body={
                    "url": url_builder.build_url(method, param_str),
                    "method": method,
                    "param": param_str,
                    "response": error.response.json()
                },
                level=log_en.ERROR))
            raise error
        except Exception as error:
            log(LogMessage(
                time=None,
                heder="Неизвестная ошибка.",
                heder_dict=error.args,
                body={
                    "url": url_builder.build_url(method, param_str),
                    "method": method,
                    "param": param_str
                },
                level=log_en.ERROR))
            raise error