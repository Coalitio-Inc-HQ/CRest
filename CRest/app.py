from fastapi import FastAPI, Body, APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.types import  IncEx
from fastapi.utils import generate_unique_id
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from fastapi.routing import APIRoute
from starlette.routing import (BaseRoute,)
from fastapi import params

from CRest.loging.logging_utility import log, LogMessage, LogHeader,log_en
import uuid
import traceback

from .settings import settings

from CRest.call.сall_parameters_decoder.сall_parameters_decoder import get_body

from .database.session_database import get_session
from .database.database_requests import *

from CRest.call.calls import CallAPIBitrix
from CRest.call.url_builders.base_url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder

from .event_bind import EventBind
from .placement_bind import PlacementBind


from CRest.call.url_builders.url_builder import UrlBuilder
from CRest.call.url_builders.base_url_builders.web_hook_url_builder import WebHookUrlBuilder, get_web_hook_url_builder_depends, get_web_hook_url_builder_init_depends
from CRest.call.url_builders.base_url_builders.local_application_url_builder import LocalApplicationUrlBuilder, get_local_application_url_builder_depends, get_local_application_url_builder_init_depends
from CRest.call.url_builders.base_url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder, get_circulation_application_url_builder_depends, get_circulation_application_url_builder_init_depends

from CRest.call.url_builders.oauth2_url_builder import OAuth2UrlBuilder, get_oauth_2_url_builder_depends

from CRest.router import BitrixRouter

from CRest.event_loop_breaker.event_loop_breaker_base import EventLoopBreakerBase

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

from fastapi.datastructures import Default

AppType = TypeVar("AppType", bound="FastAPI")


class BitrixAPIMode(enum.Enum):
    WebHook = WebHookUrlBuilder
    LocalApplication = LocalApplicationUrlBuilder
    CirculationApplication = CirculationApplicationUrlBuilder



class BitrixAPIMode(enum.Enum):
    WebHook = WebHookUrlBuilder
    LocalApplication = LocalApplicationUrlBuilder
    CirculationApplication = CirculationApplicationUrlBuilder



AppType = TypeVar("AppType", bound="FastAPI")

class BitrixAPIMode(enum.Enum):
    WebHook = WebHookUrlBuilder
    LocalApplication = LocalApplicationUrlBuilder
    CirculationApplication = CirculationApplicationUrlBuilder

class BitrixAPI:
    def __init__(
        self,
        mode: BitrixAPIMode,
        call_api_bitrix: CallAPIBitrix, 
        event_loop_breaker: EventLoopBreakerBase,
        lifespan=None, 
        routers: list[APIRouter] | None = None, 
        event_binds: list[EventBind] | None = None, 
        placement_binds: list[PlacementBind] | None = None
        ) -> None:
        
        self.event_binds = event_binds or []
        self.placement_binds = placement_binds or []
        self.call_api_bitrix = call_api_bitrix

        def lifespan_decorator(app: FastAPI):
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = "Сервер запущен.",
                            tegs = {},
                            time = None,
                            level = log_en.INFO
                    ),
                    body = {}
                )
            )
            if lifespan:
                gen = lifespan(app)
                for res in gen:
                    yield res
            else:
                yield
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = "Сервер остановлен.",
                            tegs = {},
                            time = None,
                            level = log_en.INFO
                    ),
                    body = {}
                )
            )
        self.event_loop_breaker = event_loop_breaker

        self.app = FastAPI(lifespan=lifespan_decorator)

        self.get = self.app.get
        self.head = self.app.head
        self.put = self.app.put
        self.delete = self.app.delete
        self.post = self.app.post

        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.exception_handler(Exception)
        async def exception_handler(request: Request, error: Exception):
            log(
                LogMessage(
                    header=LogHeader(
                            id = uuid.uuid4(),
                            title = "Неизвестная ошибка.",
                            tegs = {
                                "url":str(request.url),
                                "error_args": error.args
                            },
                            time = None,
                            level = log_en.ERROR
                    ),
                    body = {
                        "url":str(request.url),
                        "query_params":request.query_params._list,
                        "path_params":request.path_params,
                        "body": request.state.body if hasattr(request.state, "body") else None,
                        "error_args": error.args,
                        "traceback": traceback.format_exc()
                    }
                )
            )


        match mode:
            case BitrixAPIMode.WebHook:
                self.url_bulder_depends = get_web_hook_url_builder_depends("web_hook_settings.json")
                self.url_bulder_init_depends = get_web_hook_url_builder_init_depends("web_hook_settings.json")
            case BitrixAPIMode.LocalApplication:
                self.url_bulder_depends = get_local_application_url_builder_depends("conf.json")
                self.url_bulder_init_depends = get_local_application_url_builder_init_depends("conf.json")
            case BitrixAPIMode.CirculationApplication:
                self.url_bulder_depends = get_circulation_application_url_builder_depends(get_session)
                self.url_bulder_init_depends = get_circulation_application_url_builder_init_depends(get_session)

        async def url_bulder_init_depends_(url_builder: UrlBuilder = Depends(self.url_bulder_init_depends)) -> UrlBuilder:
            """
            TODO Наверное надо добавить вызов ошибки при некооректной установке.
            """
            try:
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
                    result = await self.call_api_bitrix.call_batch(url_builder, event_arr)

                    if "result_error" in result["result"]:
                        if type(result["result"]["result_error"]) == dict:
                            if len(result["result"]["result_error"]) != 0:
                                log(
                                    LogMessage(
                                        header=LogHeader(
                                                id = uuid.uuid4(),
                                                title = "Ошибка установки обработчиков событий.",
                                                tegs = {
                                                    "member": url_builder.get_name()
                                                },
                                                time = None,
                                                level = log_en.ERROR
                                        ),
                                        body = {
                                            "member": url_builder.get_name(),
                                            "event_binds": self.event_binds,
                                            "result": result
                                        }
                                    )
                                )
        
                        
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
                    result = await self.call_api_bitrix.call_batch(url_builder, placement_arr)
                    
                    if "result_error" in result["result"]:
                        if type(result["result"]["result_error"]) == dict:
                            if len(result["result"]["result_error"]) != 0:
                                log(
                                    LogMessage(
                                        header=LogHeader(
                                                id = uuid.uuid4(),
                                                title = "Ошибка установки мест встраивания.",
                                                tegs = {
                                                    "member": url_builder.get_name()
                                                },
                                                time = None,
                                                level = log_en.ERROR
                                        ),
                                        body = {
                                            "member": url_builder.get_name(),
                                            "placement_binds": self.placement_binds,
                                            "result": result
                                        }
                                    )
                                )

                    
            except Exception as error:
                log(
                    LogMessage(
                        header=LogHeader(
                                id = uuid.uuid4(),
                                title = "Ошибка при выполнении url_bulder_init_depends_.",
                                tegs = {
                                    "member": url_builder.get_name(),
                                    "error_args": error.args
                                },
                                time = None,
                                level = log_en.ERROR
                        ),
                        body = {
                            "member": url_builder.get_name(),
                            "event_binds": self.event_binds,
                            "placement_binds": self.placement_binds,
                            "error_args": error.args,
                            "traceback": traceback.format_exc()
                        }
                    )
                )
                raise error

        
        self.url_bulder_init_depends = url_bulder_init_depends_



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
    
    def include_router(
        self,
        router: "BitrixRouter", 
        *args,
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(generate_unique_id),
    ) -> None:

        for event in router.event_binds:
            new_event = EventBind(event=event.event, handler=prefix+event.handler)
            self.event_binds.append(new_event)

        for placement in router.placement_binds:
            new_placement = PlacementBind(title=placement.title, placement=placement.placement, handler=prefix+placement.handler)
            self.placement_binds.append(new_placement)

        router.event_loop_breaker = self.event_loop_breaker
        router.url_bulder_depends = self.url_bulder_depends
        router.url_bulder_init_depends = self.url_bulder_init_depends

        self.app.include_router(
            router.router, 
            *args,
            prefix = prefix,
            tags = tags,
            dependencies = dependencies,
            default_response_class = default_response_class,
            responses = responses,
            callbacks = callbacks,
            deprecated = deprecated,
            include_in_schema = include_in_schema,
            generate_unique_id_function = generate_unique_id_function,
        )
