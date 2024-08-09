from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request 

from src.settings import settings

from src.auth.auth_schemes import *

class BodyPreparer(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):        

        # Извлечение тела запроса
        content_type = request.headers.get("content-type")
        body = {}
        if content_type == "application/json":
            body = await request.json()
        elif content_type == "application/x-www-form-urlencoded":
            body = await decode_body_request(request)
        request.state.body = body

        # Получение аутентификации
        if settings.IS_CIRCULATION_APP:
            if "code" in request.query_params:
                # Испльзован OAuth 2.0
                pass
            elif "AUTH_ID" in body:
                # Аутентификация через фрайм
                auth = AuthFrame()
                pass
            elif "auth" in body:
                # Аутентификация через форму при событии
                pass
            else:
                # вытащить из БД
                pass
        else:
            # хук
            pass

        response = await call_next(request)


        return response