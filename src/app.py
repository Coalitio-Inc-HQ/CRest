from fastapi import FastAPI, APIRouter,Request,Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .loging.logging_utility import log, LogMessage,log_en
from .settings import settings

from src.call.сall_parameters_decoder.сall_parameters_decoder import get_body

from .database.session_database import get_session, AsyncSession
from .database.database_requests import *

from src.call.calls import CallAPIBitrix
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder

from .event_bind import EventBind
from .placement_bind import PlacementBind

from src.body_preparer import BodyPreparer

from src.call.url_builders.url_builder import UrlBuilder
from src.call.url_builders.web_hook_url_builder import WebHookUrlBuilder, get_web_hook_url_builder_depends, get_web_hook_url_builder_init_depends
from src.call.url_builders.local_application_url_builder import LocalApplicationUrlBuilder, get_local_application_url_builder_depends, get_local_application_url_builder_init_depends
from src.call.url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder, get_circulation_application_url_builder_depends, get_circulation_application_url_builder_init_depends

from src.call.url_builders.oauth2_url_builder import OAuth2UrlBuilder, get_oauth_2_url_builder_depends


import enum

from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from fastapi.params import Depends
from fastapi.types import  IncEx
from fastapi.utils import generate_unique_id
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from fastapi.routing import APIRoute

from functools import wraps


AppType = TypeVar("AppType", bound="FastAPI")

class BitrixAPIMode(enum.Enum):
    WebHook = WebHookUrlBuilder
    LocalApplication = LocalApplicationUrlBuilder
    CirculationApplication = CirculationApplicationUrlBuilder

class BitrixAPI:
    def __init__(self, mode: BitrixAPIMode, call_api_bitrix: CallAPIBitrix, lifespan=None) -> None:
        self.event_binds = []
        self.placement_binds = []
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

        self.app = FastAPI(lifespan=lifespan_decorator)

        self.get = self.app.get
        self.head = self.app.head
        self.put = self.app.put
        self.delete = self.app.delete
        self.post = self.app.post

        
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
                res = await self.call_api_bitrix.call_batch(url_builder, event_arr)
                if "result_error" in res:
                    if type(res["result_error"]) == dict:
                        if len(res["result_error"].keys()) != 0:
                            log(LogMessage(time=None, heder="Ошибка добавления обработчиков событий.",
                                heder_dict={}, body={
                                    "res": res
                                },
                                level=log_en.ERROR))

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
                res = await self.call_api_bitrix.call_batch(url_builder, placement_arr)

                if "result_error" in res:
                    if type(res["result_error"]) == dict:
                        if len(res["result_error"].keys()) != 0:
                            log(LogMessage(time=None, heder="Ошибка добавления обработчиков встраисвния.",
                                heder_dict={}, body={
                                    "res": res
                                },
                                level=log_en.ERROR))
            return url_builder
        self.url_bulder_init_depends = url_bulder_init_depends_

        # Убрать в последствии
        router = APIRouter()
        build_app(router, self.url_bulder_depends, self.url_bulder_init_depends, self.call_api_bitrix)
        self.app.include_router(router, tags=["webhook"])



    def add_event_bind(
        self,
        event: str,
        *,
        path: str| None = None,
        response_model: Any = None,
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, enum.Enum]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[IncEx] = None,
        response_model_exclude: Optional[IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: Optional[str] = None,
        callbacks: Optional[List[APIRoute]] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
    ) -> Callable[[Callable], Callable]:
        
        if not path:
            path = "/" + event 
        self.event_binds.append(EventBind(event=event, handler=path))

        return self.app.router.post(
            path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function,
        )
    
    
    def add_placement_bind(
        self,
        placement: str,
        title: str,
        *,
        path: str| None = None,
        response_model: Any = None,
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, enum.Enum]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[IncEx] = None,
        response_model_exclude: Optional[IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: Optional[str] = None,
        callbacks: Optional[List[APIRoute]] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
    ) -> Callable[[Callable], Callable]:

        if not path:
            path = "/" + placement 
        self.placement_binds.append(PlacementBind(title=title, placement=placement, handler=path))        

        return self.app.router.post(
            path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function,
        )        
    

def build_app(router: APIRouter, base_auth =None, url_bulder_init_depends=None, call_api_bitrix = None): 
    
    @router.head("/install")
    async def init_head():
        pass

    @router.head("/index")
    async def index_head():
        pass
    
    @router.post("/install", response_class=HTMLResponse)
    async def install_post(url_builder = Depends(url_bulder_init_depends), body: dict | None = Depends(get_body)):
        url_builder =url_builder

        if (body["PLACEMENT"]=="DEFAULT"):
            
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
    async def index_get(url_builder = Depends(get_oauth_2_url_builder_depends)):

        res = await call_api_bitrix.call_method(url_builder,"crm.contact.add",
                                                    {
                                                        "FIELDS":{
                                                            "NAME": "Иван",
                                                            "LAST_NAME": "Петров",
                                                            "EMAIL":[
                                                                {
                                                                    "VALUE": "mail@example.com",
                                                                    "VALUE_TYPE": "WORK"
                                                                }
                                                            ],
                                                            "PHONE":[
                                                                {
                                                                    "VALUE": "555888",
                                                                    "VALUE_TYPE": "WORK"
                                                                }
                                                            ]
                                                        }
                                                    })
        return {"res":res}

    @router.post("/index")
    async def index_post(url_builder = Depends(base_auth),):

        res = await call_api_bitrix.call_method(url_builder,"crm.contact.add",
                                                    {
                                                        "FIELDS":{
                                                            "NAME": "Иван",
                                                            "LAST_NAME": "Петров",
                                                            "EMAIL":[
                                                                {
                                                                    "VALUE": "mail@example.com",
                                                                    "VALUE_TYPE": "WORK"
                                                                }
                                                            ],
                                                            "PHONE":[
                                                                {
                                                                    "VALUE": "555888",
                                                                    "VALUE_TYPE": "WORK"
                                                                }
                                                            ]
                                                        }
                                                    })

        res1 = await call_api_bitrix.call_batch(
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
        res2 = await call_api_bitrix.call_batch(url_builder, arr, True)


        return {"res": res, "res1": res1, "res2": res2}


