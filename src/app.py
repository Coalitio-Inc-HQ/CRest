from fastapi import FastAPI, Body, APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.types import  IncEx
from fastapi.utils import generate_unique_id
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from fastapi.routing import APIRoute

from .loging.logging_utility import log, LogMessage,log_en
from .settings import settings

from src.call.сall_parameters_decoder.сall_parameters_decoder import get_body

from .database.session_database import get_session
from .database.database_requests import *

from src.call.calls import CallAPIBitrix
from call.url_builders.base_url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder

from .event_bind import EventBind
from .placement_bind import PlacementBind

from src.body_preparer import BodyPreparer

from src.call.url_builders.url_builder import UrlBuilder
from call.url_builders.base_url_builders.web_hook_url_builder import WebHookUrlBuilder, get_web_hook_url_builder_depends, get_web_hook_url_builder_init_depends
from call.url_builders.base_url_builders.local_application_url_builder import LocalApplicationUrlBuilder, get_local_application_url_builder_depends, get_local_application_url_builder_init_depends
from call.url_builders.base_url_builders.circulation_application_url_builder import CirculationApplicationUrlBuilder, get_circulation_application_url_builder_depends, get_circulation_application_url_builder_init_depends

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
        lifespan=None, 
        routers: list[APIRouter] | None = None, 
        event_binds: list[EventBind] | None = None, 
        placement_binds: list[PlacementBind] | None = None
        ) -> None:
        
        self.event_binds = event_binds or []
        self.placement_binds = placement_binds or []
        self.call_api_bitrix = call_api_bitrix

        def lifespan_decorator(app: FastAPI):
            log(LogMessage(time=None, header="Сервер запущен.", header_dict=None, body=None, level=log_en.INFO))
            if lifespan:
                gen = lifespan(app)
                for res in gen:
                    yield res
            else:
                yield
            log(LogMessage(time=None, header="Сервер остановлен.", header_dict=None, body=None, level=log_en.INFO))

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
            log(LogMessage(time=None, header="Неизвестная ошибка.",
                           header_dict=error.args, body={
                               "url": str(request.url), "query_params": request.query_params._list,
                               "path_params": request.path_params,
                           },
                           level=log_en.ERROR))

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
                    await self.call_api_bitrix.call_batch(url_builder, event_arr)
                    log(LogMessage(time=None, header="Events bound successfully.", header_dict=None, body={"events": [event.event for event in self.event_binds]}, level=log_en.INFO))
                        
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
                    log(LogMessage(time=None, header="Placements bound successfully.", header_dict=None, body={"placements": [placement.placement for placement in self.placement_binds]}, level=log_en.INFO))
            
            except Exception as e:
                log(LogMessage(time=None, header="Error during URL builder.", header_dict=str(e), body=None, level=log_en.ERROR))
                raise

        
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
    



