from fastapi import FastAPI, Body, APIRouter,Request,Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.datastructures import Default

from .loging.logging_utility import log, LogMessage,log_en
from .settings import settings

from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request, get_body

from .database.session_database import get_session, AsyncSession
from .database.database_requests import *

from src.call.calls import CallAPIBitrix
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder

from .event_bind import EventBind
from .placement_bind import PlacementBind

from src.body_preparer import BodyPreparer

from src.call.call_director import CallDirectorBarrelStrategy

from src.call.url_builders.oauth2_url_builder import OAuth2UrlBuilder

from src.call.url_builders.url_builder import UrlBuilder
from src.call.url_builders.web_hook_url_builder import WebHookUrlBuilder, get_web_hook_url_builder_depends, get_web_hook_url_builder_init_depends
from src.call.url_builders.local_application_url_builder import LocalApplicationUrlBuilder, get_local_application_url_builder_depends, get_local_application_url_builder_init_depends
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder, get_circulation_application_url_builder_depends, get_circulation_application_url_builder_init_depends

import enum

class BitrixAPIMode(enum.Enum):
    WebHook = WebHookUrlBuilder
    LocalApplication = LocalApplicationUrlBuilder
    CirculationApplication = CirculationApplicationUrlBuilder

from fastapi import FastAPI, Body, APIRouter,Request,Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.datastructures import Default

from .loging.logging_utility import log, LogMessage,log_en
from .settings import settings

from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request, get_body

from .database.session_database import get_session, AsyncSession
from .database.database_requests import *

from src.call.calls import CallAPIBitrix
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder

from .event_bind import EventBind
from .placement_bind import PlacementBind

from src.body_preparer import BodyPreparer

from src.call.call_director import CallDirectorBarrelStrategy

from src.call.url_builders.oauth2_url_builder import OAuth2UrlBuilder

from src.call.url_builders.url_builder import UrlBuilder
from src.call.url_builders.web_hook_url_builder import WebHookUrlBuilder, get_web_hook_url_builder_depends, get_web_hook_url_builder_init_depends
from src.call.url_builders.local_application_url_builder import LocalApplicationUrlBuilder, get_local_application_url_builder_depends, get_local_application_url_builder_init_depends
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder, get_circulation_application_url_builder_depends, get_circulation_application_url_builder_init_depends

import enum

class BitrixAPIMode(enum.Enum):
    WebHook = WebHookUrlBuilder
    LocalApplication = LocalApplicationUrlBuilder
    CirculationApplication = CirculationApplicationUrlBuilder

from functools import wraps

class BitrixAPI:
    def __init__(self, mode: BitrixAPIMode, call_api_bitrix: CallAPIBitrix, lifespan=None, routers: list[APIRouter] | None = None, event_binds: list[EventBind] | None = None, placement_binds: list[PlacementBind] | None = None) -> None:
        self.event_binds = event_binds or []
        self.placement_binds = placement_binds or []
        self.call_api_bitrix = call_api_bitrix

        def lifespan_decorator(app: FastAPI):
            log(LogMessage(time=None, heder="Сервер запущен.", heder_dict=None, body=None, level=log_en.INFO))
            if lifespan:
                gen = lifespan(app)
                for res in gen:
                    yield res
            else:
                yield
            log(LogMessage(time=None, heder="Сервер остановлен.", heder_dict=None, body=None, level=log_en.INFO))

        self.app = FastAPI()

        # Убрать в последствии
        for rout in routers:
            self.app.include_router(rout)

        self.app.add_middleware(BodyPreparer)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.exception_handler(Exception)
        async def exception_handler(request: Request, error: Exception):
            log(LogMessage(time=None, heder="Неизвестная ошибка.",
                           heder_dict=error.args, body={
                               "url": str(request.url), "query_params": request.query_params._list,
                               "path_params": request.path_params,
                           },
                           level=log_en.ERROR))

        match mode:
            case BitrixAPIMode.WebHook:
                self.url_bulder_depends = get_web_hook_url_builder_depends()
                self.url_bulder_init_depends = get_web_hook_url_builder_init_depends()
            case BitrixAPIMode.LocalApplication:
                self.url_bulder_depends = get_local_application_url_builder_depends("conf.json")
                self.url_bulder_init_depends = get_local_application_url_builder_init_depends("conf.json")
            case BitrixAPIMode.CirculationApplication:
                self.url_bulder_depends = get_circulation_application_url_builder_depends(get_session)
                self.url_bulder_init_depends = get_circulation_application_url_builder_init_depends(get_session)

        async def url_bulder_init_depends_(url_builder: UrlBuilder = Depends(self.url_bulder_init_depends)) -> UrlBuilder:
            if self.event_binds:
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
                await self.call_api_bitrix.call_batch(url_builder, event_arr)
                # добавить вывод ошибок

            if self.placement_binds:
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
                await self.call_api_bitrix.call_batch(url_builder, placement_arr)
                # добавить вывод ошибок
            return url_builder
        self.url_bulder_init_depends = url_bulder_init_depends_

        # Убрать в последствии
        router = APIRouter()
        self.build_app(router)
        self.app.include_router(router, tags=["webhook"])

    def install_decorator(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper

    def index_decorator(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper

    def build_app(self, router: APIRouter):

        @router.head("/install")
        async def init_head():
            pass

        @router.head("/index")
        async def index_head():
            pass

        @router.post("/install", response_class=HTMLResponse)
        @self.install_decorator
        async def install_post(url_builder: UrlBuilder = Depends(self.url_bulder_init_depends), body: dict | None = Depends(get_body)):
            if (body["PLACEMENT"] == "DEFAULT"):
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
                        installation has been finished.
                </body>
                """
            else:
                return """
                <body>
                        Installation has been fail.
                </body>
                """

        @router.get("/index")
        @self.index_decorator
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
        async def index_post(url_builder: UrlBuilder = Depends(self.url_bulder_depends)):

            res = await self.call_api_bitrix.call_method(url_builder, "crm.contact.add",
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

            res1 = await self.call_api_bitrix.call_batch(
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
            res2 = await self.call_api_bitrix.call_batch(url_builder, arr, True)

            return {"res": res, "res1": res1, "res2": res2}
