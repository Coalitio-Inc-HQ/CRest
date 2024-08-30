from httpx import AsyncClient, HTTPStatusError
from typing import Any

from CRest.loging.logging_utility import log, LogMessage, LogHeader,log_en,filter_array_to_str,filter_dict_to_str
import uuid
import traceback

from CRest.call.url_builders.url_builder import UrlBuilder
from CRest.call.url_builders.url_builder import ExceptionRefreshAuth


async def call_execute(url_builder: UrlBuilder, method: str, param_str: str, body: dict | None = None) -> Any:
    """
    Осуществляет выполнение запроса с учётом переадрисации и обновления токена.
    """
    async with AsyncClient(timeout=10.0) as clinet:
        try:
            response = await clinet.post(url_builder.build_url(method, param_str), json=body)

            if response.status_code == 401:
                if url_builder.is_reauth:
                    await url_builder.update_auth()
                    response = await clinet.post(url_builder.build_url(method, param_str), json=body)
            elif response.status_code == 302:
                await url_builder.update_domain(response.headers['Location'])
                response = await clinet.post(url_builder.build_url(method, param_str), json=body)

            response.raise_for_status()
            return response.json()

        except ExceptionRefreshAuth as error:
            raise error
        except HTTPStatusError as error:
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = f"Ошибка выполнения запроса. {error.response.status_code}",
                            tegs = {
                                "member": url_builder.get_name(),
                                "method": method,
                                "status_code": error.response.status_code,
                                "error_args":error.args
                            },
                            time = None,
                            level = log_en.ERROR
                    ),
                    body = {
                        "url": url_builder.build_url(method, param_str),
                        "method": method,
                        "param": param_str,
                        "response": error.response.json(),
                        "member": url_builder.get_name(),
                        "error_args":error.args,
                        "traceback": traceback.format_exc()
                    }
                )
            )
            raise error
        except Exception as error:
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = "Неизвестная ошибка.",
                            tegs = {
                                "member": url_builder.get_name(),
                                "method": method,
                                "error_args":error.args
                            },
                            time = None,
                            level = log_en.ERROR
                    ),
                    body = {
                        "url": url_builder.build_url(method, param_str),
                        "method": method,
                        "param": param_str,
                        "member": url_builder.get_name(),
                        "error_args":error.args,
                        "traceback": traceback.format_exc()
                    }
                )
            )
            raise error