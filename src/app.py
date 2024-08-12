from fastapi import FastAPI, Body, APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import json
from functools import wraps

from .loging.logging_utility import log, LogMessage, log_en
from .settings import settings

from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request, get_body

from .database.session_database import get_session, AsyncSession
from .database.database_requests import *

from src.call.calls import CallAPIBitrix
from src.call.call_director import CallDirectorBarrelStrategy
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder
from src.call.url_builders.local_application_url_builder import LocalApplicationUrlBuilder
from src.call.url_builders.oauth2_url_builder import OAuth2UrlBuilder

from .event_bind import EventBind
from .placement_bind import PlacementBind

from src.body_preparer import BodyPreparer


class AppBuilder:
    def __init__(self, routers: list[APIRouter] | None = None, event_binds: list[EventBind] | None = None, placement_binds: list[PlacementBind] | None = None):
        self.routers = routers
        self.event_binds = event_binds
        self.placement_binds = placement_binds
        self.app = None

    def install_decorator(self, func):
        @wraps(func)
        async def wrapper(DOMAIN: str, PROTOCOL: int, LANG: str, APP_SID: str, request: Request, session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)):
            auth = AuthDTO(
                lang=LANG,
                app_id=APP_SID,
                access_token=body["AUTH_ID"],
                expires=None,
                expires_in=int(body["AUTH_EXPIRES"]),
                scope=None,
                domain=DOMAIN,
                status=body["status"],
                member_id=body["member_id"],
                user_id=None,
                refresh_token=body["REFRESH_ID"],
            )

            bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())

            with open("conf.json", 'w', encoding='utf-8') as f:
                f.write(auth.model_dump_json())
            url_builder = LocalApplicationUrlBuilder("conf.json")

            return await func(bitrix_api, url_builder, auth, session, body)
        return wrapper

    def index_decorator(self, func):
        @wraps(func)
        async def wrapper(DOMAIN: str, PROTOCOL: int, LANG: str, APP_SID: str, request: Request, session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)):
            url_builder = LocalApplicationUrlBuilder("conf.json")
            bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())

            return await func(bitrix_api, url_builder, body)
        return wrapper

    def build(self) -> FastAPI:
        async def lifespan(app: FastAPI):
            log(LogMessage(time=None, heder="Сервер запущен.", heder_dict=None, body=None, level=log_en.INFO))
            yield
            log(LogMessage(time=None, heder="Сервер остановлен.", heder_dict=None, body=None, level=log_en.INFO))

        self.app = FastAPI(lifespan=lifespan)

        self.app.add_middleware(BodyPreparer)

        @self.app.exception_handler(Exception)
        async def exception_handler(request: Request, error: Exception):
            log(LogMessage(time=None, heder="Неизвестная ошибка.", 
                        heder_dict=error.args, body={
                            "url": str(request.url),
                            "query_params": request.query_params._list,
                            "path_params": request.path_params,
                        },
                        level=log_en.ERROR))

        print("BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        if self.routers:
            for item in self.routers:
                self.app.include_router(item)

        router = APIRouter()

        @router.head("/install")
        async def init_head():
            pass

        @router.head("/index")
        async def index_head():
            pass

        @router.post("/install", response_class=HTMLResponse)
        @self.install_decorator
        async def install_post(bitrix_api, url_builder, auth, session, body):
            if body["PLACEMENT"] == "DEFAULT":
                event_arr = []
                for event in self.event_binds:
                    event_arr.append(
                        {
                            "method": "event.bind",
                            "params": {
                                "event": event.event,
                                "handler": settings.APP_HANDLER_ADDRESS + event.handler
                            }
                        }
                    )
                await bitrix_api.call_batch(url_builder, event_arr)
                
                placement_arr = []
                for placement in self.placement_binds:
                    placement_arr.append(
                        {
                            "method": "placement.bind",
                            "params": {
                                "PLACEMENT": placement.placement,
                                "HANDLER": settings.APP_HANDLER_ADDRESS + placement.handler,
                                "TITLE": placement.title
                            }
                        }
                    )
                await bitrix_api.call_batch(url_builder, placement_arr)

                return """
                <head>
                    <script src="//api.bitrix24.com/api/v1/"></script>
                    <script>
                        BX24.init(function(){
                            BX24.installFinish();
                        });
                    </script>
                </head>
                <body>
                    Installation has been finished.
                </body>
                """
            else:
                return """
                <body>
                    Installation has failed.
                </body>
                """

        @router.get("/index")
        async def index_get(code: str, domain: str, member_id: str, scope: str, server_domain: str, request: Request, session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)):
            bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())

            url_builder = OAuth2UrlBuilder(code)
            await url_builder.get_auth()

            res = await bitrix_api.call_method(url_builder, "crm.contact.add",
                                               {
                                                   "FIELDS": {
                                                       "NAME": "Иван",
                                                       "LAST_NAME": "Петров",
                                                       "EMAIL": [
                                                           {
                                                               "VALUE": "mail@example.com",
                                                               "VALUE_TYPE": "WORK"
                                                           }
                                                       ],
                                                       "PHONE": [
                                                           {
                                                               "VALUE": "555888",
                                                               "VALUE_TYPE": "WORK"
                                                           }
                                                       ]
                                                   }
                                               })

            return {"res": res}

        @router.post("/index")
        @self.index_decorator
        async def index_post(bitrix_api, url_builder, body):
            res = await bitrix_api.call_method(url_builder, "crm.contact.add",
                                               {
                                                   "FIELDS": {
                                                       "NAME": "Иван",
                                                       "LAST_NAME": "Петров",
                                                       "EMAIL": [
                                                           {
                                                               "VALUE": "mail@example.com",
                                                               "VALUE_TYPE": "WORK"
                                                           }
                                                       ],
                                                       "PHONE": [
                                                           {
                                                               "VALUE": "555888",
                                                               "VALUE_TYPE": "WORK"
                                                           }
                                                       ]
                                                   }
                                               })

            res1 = await bitrix_api.call_batch(
                url_builder,
                [
                    {
                        "method": "crm.contact.add",
                        "params": {
                            "FIELDS": {
                                "NAME": "Иван1",
                                "LAST_NAME": "Петров1"
                            }
                        }
                    },
                    {
                        "method": "crm.contact.add",
                        "params": {
                            "FIELDS": {
                                "NAME": "Иван2",
                                "LAST_NAME": "Петров2"
                            }
                        }
                    }
                ])

            arr = []
            for i in range(46):
                arr.append(
                    {
                        "method": "crm.contact.add",
                        "params": {
                            "FIELDS": {
                                "NAME": f"Иван{i}",
                                "LAST_NAME": f"Петров{i}"
                            }
                        }
                    }
                )

            arr.insert(10,
                       {
                           "method": "crm.contact.add",
                           "params": {
                               "FIELDS": "NAME"
                           }
                       })
            res2 = await bitrix_api.call_batch(url_builder, arr, True)

            return {"res": res, "res1": res1, "res2": res2}

        self.app.include_router(router, tags=["webhook"])

        return self.app
