from httpx import AsyncClient, HTTPStatusError
from typing import Any
from src.loging.logging_utility import log, LogMessage, log_en

from src.call.url_builder import UrlBuilder


async def call_execute(url_builder: UrlBuilder, method: str, param_str: str) -> Any:
    """
    Осуществляет выполнение запроса с учётом переадрисации и обновления токена.
    """
    async with AsyncClient(timeout=10.0) as clinet:
        try:
            response = await clinet.post(url_builder.build_url(method, param_str))

            if response.status_code == 401:
                if url_builder.is_reauth:
                    await refresh_auth(url_builder)
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


class ExceptionRefreshAuth(Exception):
    error: str


async def refresh_auth(url_builder: UrlBuilder) -> None:
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
    """
    try:
        async with AsyncClient(timeout=10.0) as clinet:
            result = await clinet.post(url_builder.build_url_update_auth())
            result.raise_for_status()
            result = result.json()

        if "error" in result:
            log(LogMessage(
                time=None,
                heder="Ошибка при выполнении refresh_auth.",
                heder_dict=result["error"],
                body={
                    "auth_url": url_builder.build_url_update_auth(),
                    "result": result
                },
                level=log_en.ERROR))
            raise ExceptionRefreshAuth(error=result["error"])

        await url_builder.update_auth(result["access_token"], int(result["expires_in"]), result["client_endpoint"], result["refresh_token"])

    except ExceptionRefreshAuth as error:
        raise error
    except HTTPStatusError as error:
        log(LogMessage(
            time=None,
            heder=f"Ошибка при выполнении refresh_auth. {
                error.response.status_code}",
            heder_dict=error.args,
            body={
                "url": url_builder.build_url_update_auth(),
                "response": error.response.json()
            },
            level=log_en.ERROR))
        ExceptionRefreshAuth(error=str(error.response.status_code))
    except Exception as error:
        log(LogMessage(
            time=None,
            heder="Ошибка при выполнении refresh_auth.",
            heder_dict=error.args,
            body={"auth_url": url_builder.build_url_update_auth()},
            level=log_en.ERROR))
        raise ExceptionRefreshAuth(error="undefined")
