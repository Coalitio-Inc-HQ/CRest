from fastapi import APIRouter, Depends
from typing import Optional, List, Union, Type, Dict, Any, Sequence, Callable
from enum import Enum

from fastapi import params
from fastapi.datastructures import Default
from fastapi.utils import (generate_unique_id,)
from starlette.responses import JSONResponse, Response
from starlette.routing import (BaseRoute,)
from starlette.routing import Mount as Mount  # noqa
from starlette.types import ASGIApp, Lifespan
from fastapi.types import  IncEx

from typing import Literal

from fastapi.routing import APIRoute

from CRest.event_bind import EventBind
from CRest.placement_bind import PlacementBind
from .robot_bind import RobotBind

class BitrixRouter():
    def __init__(
                self, 
                parent,
                *args, 
                prefix: str = "",
                tags: Optional[List[Union[str, Enum]]] = None,
                dependencies: Optional[Sequence[params.Depends]] = None,
                default_response_class: Type[Response] = Default(JSONResponse),
                responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
                callbacks: Optional[List[BaseRoute]] = None,
                routes: Optional[List[BaseRoute]] = None,
                redirect_slashes: bool = True,
                default: Optional[ASGIApp] = None,
                dependency_overrides_provider: Optional[Any] = None,
                route_class: Type[APIRoute] = APIRoute,
                on_startup: Optional[Sequence[Callable[[], Any]]] = None,
                on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
                lifespan: Optional[Lifespan[Any]] = None,
                deprecated: Optional[bool] = None,
                include_in_schema: bool = True,
                generate_unique_id_function: Callable[[APIRoute], str] = Default(generate_unique_id),
                ) -> None:
        
        self.router = APIRouter(
            prefix=prefix, tags=tags,dependencies=dependencies, default_response_class=default_response_class,
            responses=responses, callbacks=callbacks, routes=routes, redirect_slashes=redirect_slashes,
            default=default, dependency_overrides_provider=dependency_overrides_provider, route_class=route_class,
            on_startup=on_startup, on_shutdown=on_shutdown, lifespan=lifespan,deprecated=deprecated,
            include_in_schema=include_in_schema, generate_unique_id_function=generate_unique_id_function
        )

        self.call_api_bitrix = parent.call_api_bitrix
        self.url_bulder_depends = parent.url_bulder_depends
        self.url_bulder_init_depends = parent.url_bulder_init_depends
        self.event_loop_breaker = parent.event_loop_breaker
        self.routers = []

        parent.routers.append(self)

        self.get = self.router.get
        self.head = self.router.head
        self.put = self.router.put
        self.delete = self.router.delete
        self.post = self.router.post

        self.event_binds = []
        self.placement_binds = []
        self.robot_binds = []

    def add_event_bind(
        self,
        event: str,
        *,
        path: str| None = None,
        response_model: Any = None,
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
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
        rout_path = path
        path = self.router.prefix + path
        self.event_binds.append(EventBind(event=event, handler=path))

        return self.router.post(
            rout_path,
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
        tags: Optional[List[Union[str, Enum]]] = None,
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
        rout_path = path
        path = self.router.prefix + path
        self.placement_binds.append(PlacementBind(title=title, placement=placement, handler=path))        

        return self.router.post(
            rout_path,
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
    

    def add_robot_bind(
        self,
        code: str,
        robot_name:str,
        *,
        path: str| None = None,
        auth_user_id:str = "1",
        use_subscriptin: Literal["N","Y"]="N",
        proprtes: Any = None,
        use_placment: Literal["N","Y"] = "N",
        placment_handler: str | None = None,
        return_proprtes: Any = None,

        response_model: Any = None,
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
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
        if use_placment == "Y" and placment_handler==None:
            raise Exception("use_placment=Y, placment_handler=None")

        if not path:
            path = "/" + code 
        rout_path = path
        path = self.router.prefix + path
        self.robot_binds.append(RobotBind(
            code = code,
            handler = path,
            auth_user_id = auth_user_id ,
            name = robot_name,
            use_subscriptin = use_subscriptin,
            proprtes = proprtes,
            use_placment = use_placment,
            placment_handler = placment_handler,
            return_proprtes = return_proprtes,
            ))        

        return self.router.post(
            rout_path,
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



    def build_router(self) -> None:
        for item in self.routers:
            item.build_router()

            for event in item.event_binds:
                new_event = EventBind(event=event.event, handler=self.router.prefix+event.handler)
                self.event_binds.append(new_event)

            for placement in item.placement_binds:
                new_placement = PlacementBind(title=placement.title, placement=placement.placement, handler=self.router.prefix+placement.handler)
                self.placement_binds.append(new_placement)

            for robot in item.robot_binds:
                new_robot = RobotBind(
                                code = robot.code,
                                handler =self.router.prefix+robot.handler,
                                auth_user_id = robot.auth_user_id ,
                                name = robot.name,
                                use_subscriptin = robot.use_subscriptin,
                                proprtes = robot.proprtes,
                                use_placment = robot.use_placment,
                                placment_handler = robot.placment_handler,
                                return_proprtes = robot.return_proprtes,
                                )
                self.robot_binds.append(new_robot)

            self.router.include_router(item.router)

