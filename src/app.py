from fastapi import FastAPI, Body, APIRouter,Request,Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.datastructures import Default

import json

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

from src.call.url_builders.local_application_url_builder import LocalApplicationUrlBuilder

def build_app(routers: list[APIRouter] | None = None , event_binds: list[EventBind] | None = None, placement_binds: list[PlacementBind] | None = None) -> FastAPI:

    async def lifespan(app: FastAPI):
        log(LogMessage(time=None,heder="Сервер запущен.", heder_dict=None,body=None,level=log_en.INFO))
        yield
        log(LogMessage(time=None,heder="Сервер остановлен.", heder_dict=None,body=None,level=log_en.INFO))

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(BodyPreparer)

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, error: Exception):
        log(LogMessage(time=None,heder="Неизвестная ошибка.", 
                    heder_dict=error.args,body=
                    {"url":str(request.url),"query_params":request.query_params._list,
                        "path_params":request.path_params,
                        },
                        level=log_en.ERROR))
        

    print("BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    if routers:
        for item in routers:
            app.include_router(item)


    router = APIRouter()


    @router.head("/install")
    async def init_head():
        pass


    @router.head("/index")
    async def index_head():
        pass


    @router.post("/install", response_class=HTMLResponse)
    async def install_post (DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str,request: Request,  session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)):
        
        form = await request.form() 
        print(form)

        print(body)

        if (body["PLACEMENT"]=="DEFAULT"):
            auth = AuthDTO(
                lang=LANG,
                app_id=APP_SID,

                access_token = body["AUTH_ID"],
                expires=None,
                expires_in = int(body["AUTH_EXPIRES"]),
                scope=None,
                domain=DOMAIN,
                status= body ["status"],
                member_id = body["member_id"],
                user_id=None,
                refresh_token = body["REFRESH_ID"],
            )


            bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())

            # Тиражное приложение
            # await insert_auth(session, auth)
            # url_builder = CirculationApplicationUrlBuilder(auth,session)

            # Локальное приложение
            with open("conf.json", 'w', encoding='utf-8') as f:
                f.write(auth.model_dump_json())
            url_builder = LocalApplicationUrlBuilder("conf.json")

            
            if event_binds:
                event_arr = []
                for event in event_binds:
                    event_arr.append(
                        {
                            "method": "event.bind",
                            "params":{
                                "event": event.event,
                                "handler": settings.APP_HANDLER_ADDRESS+event.handler
                            }
                        }
                    )             
                await bitrix_api.call_batch(url_builder, event_arr)
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! добавить вывод ошибок

            if placement_binds:
                placement_arr = []
                for placement in placement_binds:
                    placement_arr.append(
                        {
                            "method": "placement.bind",
                            "params":{
                                "PLACEMENT": placement.placement,
                                "HANDLER": settings.APP_HANDLER_ADDRESS+placement.handler,
                                "TITLE": placement.title
                            }
                        }
                    )
                await bitrix_api.call_batch(url_builder, placement_arr)
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! добавить вывод ошибок

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
    async def index_get(code:str, domain:str, member_id:str, scope:str, server_domain: str, request: Request, session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)):

        bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())

        url_builder = OAuth2UrlBuilder(code)
        await url_builder.get_auth()

        res = await bitrix_api.call_method(url_builder,"crm.contact.add",
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
    async def index_post(DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str, request: Request, session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)):

        # Тиражное приложение
        # auth = await get_auth_by_member_id(session=session, member_id=body["member_id"])
        # url_builder = CirculationApplicationUrlBuilder(auth,session)

        # Локальное приложение
        url_builder = LocalApplicationUrlBuilder("conf.json")

        bitrix_api = CallAPIBitrix(CallDirectorBarrelStrategy())
          
        res = await bitrix_api.call_method(url_builder,"crm.contact.add",
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

    app.include_router(router, tags=["webhook"])

    return app