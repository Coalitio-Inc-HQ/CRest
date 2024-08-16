from CRest.database.schemes import AuthDTO
from CRest.settings import settings
from CRest.database.database_requests import *

from httpx import AsyncClient, HTTPStatusError
from typing import Any

from CRest.loging.logging_utility import log, LogMessage, LogHeader,log_en,filter_array_to_str,filter_dict_to_str
import uuid
import traceback


class ExceptionRefreshAuth(Exception):
    error: str


class UrlBuilder:
    """
    Абстрацный класс сборщика url
    """
    def __init__(self, is_reauth: bool, is_redomain: bool):
        self.strategy = "json"
        self.is_reauth = is_reauth
        self.is_redomain = is_redomain


    def build_url(self, method:str, params: str) -> str:
        pass


    async def update_auth(self) -> None:
        pass


    async def update_domain(self, domain: str) -> None:
        pass


    def get_name(self) -> str:
        pass


    def bild_url(self, method: str, params_str: str) -> str:
        """
        Собирает url для вызова метода.
        """
        pass
    

    # @property
    # async def member_id(self) -> str | None:
    #     """
    #     Получает id портала.
    #     """
    #     pass


    # @property
    # async def user_id(self) -> str:
    #     """
    #     Получает id пользователя.
    #     """
    #     pass
    
    
    # @property
    # async def is_admin(self) -> bool:
    #     """
    #     Проверяет является ли пользователь адменистратором.
    #     """
    #     pass


    @staticmethod
    async def refresh_auth(params: dict) -> dict:
        """
        Осуществляет обновление токена авторизации.

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

        Коды http
        'undefined' => 'Неизвестная ошибка.'

        Параметры:
        {
            "client_id": "app.66b16e2.915",
            "grant_type": "refresh_token",
            "client_secret": "XTpVYlUws6WVQog",
            "refresh_token": "d3400000001605407fd72e58"
        }
        или
        {
            "grant_type":"authorization_code",
            "client_id":"app.573ad8a0346747.09223434",
            "client_secret":"LJSl0lNB76B5YY6u0YVQ3AW0DrVADcRTwVr4y99PXU1BWQybWK",
            "code":"avmocpghblyi01m3h42bljvqtyd19"
        }

        Возращяет:
        {
            "access_token": "2047b86600702a5a006ffd34000000",
            "expires": 1723352864,
            "expires_in": 3600,
            "scope": "app",
            "domain": "oauth.bitrix.info",
            "server_endpoint": "https://oauth.bitrix.info/rest/",
            "status": "F",
            "client_endpoint": "https://b24-0uus9h.bitrix24.ru/rest/",
            "member_id": "5880708e7a2166775",
            "user_id": 1,
            "refresh_token": "10c6df6600702a5a006ffd34000000016058e49d15"
        }
        """
        try:
            async with AsyncClient(timeout=10.0) as clinet:
                result = await clinet.post("https://oauth.bitrix.info/oauth/token/", data=params)
                result.raise_for_status()
                result = result.json()

            if "error" in result:
                log(
                    LogMessage(
                        header=LogHeader(
                                id = uuid.uuid4(),
                                title = "Ошибка при выполнении refresh_auth.",
                                tegs = {
                                    "paras": params
                                },
                                time = None,
                                level = log_en.ERROR
                        ),
                        body = {
                            "paras": params,
                            "result":result
                        }
                    )
                )
                raise ExceptionRefreshAuth(error=result["error"])
            
            return result

        except ExceptionRefreshAuth as error:
            raise error
        except HTTPStatusError as error:
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = f"Ошибка при выполнении refresh_auth. {error.response.status_code}",
                            tegs = {
                                "paras": params,
                                "status_code": error.response.status_code,
                                "error_args":error.args
                            },
                            time = None,
                            level = log_en.ERROR
                    ),
                    body = {
                        "paras": params,
                        "status_code": error.response.status_code,
                        "response": error.response.json(),
                        "error_args":error.args,
                        "traceback": traceback.format_exc()
                    }
                )
            )
            ExceptionRefreshAuth(error=str(error.response.status_code))
        except Exception as error:
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = "Неизвестная ошибка при выполнении refresh_auth.",
                            tegs = {
                                "paras": params,
                                "error_args":error.args
                            },
                            time = None,
                            level = log_en.ERROR
                    ),
                    body = {
                        "paras": params,
                        "error_args":error.args,
                        "traceback": traceback.format_exc()
                    }
                )
            )
            raise ExceptionRefreshAuth(error="undefined")


