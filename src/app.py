from fastapi import FastAPI, Body, APIRouter,Request,Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .loging.logging_utility import log, LogMessage,log_en
from .settings import settings
from .utils import decode_auth

from .database.session_database import get_session, AsyncSession
from .database.database_requests import *

from .call.calls import call_method, call_batch, get_list
from .call.url_builder import CirculationApplicationUrlBuilder

from .event_bind import EventBind

def build_app(event_binds: list[EventBind] | None = None) -> FastAPI:

    async def lifespan(app: FastAPI):
        log(LogMessage(time=None,heder="Сервер запущен.", heder_dict=None,body=None,level=log_en.INFO))
        yield
        log(LogMessage(time=None,heder="Сервер остановлен.", heder_dict=None,body=None,level=log_en.INFO))

    app = FastAPI(lifespan=lifespan)

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

    for event in event_binds:
        app.include_router(event.hendler_router)

    router = APIRouter()


    @router.head("/install")
    async def init_head():
        pass


    @router.head("/index")
    async def index_head():
        pass


    @router.post("/install", response_class=HTMLResponse)
    async def install_post (DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str,request: Request, session: AsyncSession = Depends(get_session)):
        auth_dict = decode_auth(str(await request.body()))

        print(auth_dict)

        if (auth_dict["PLACEMENT"]=="DEFAULT"):
            auth = AuthDTO(
                access_token = auth_dict["AUTH_ID"],
                expires_in = auth_dict["AUTH_EXPIRES"],
                refresh_token = auth_dict["REFRESH_ID"],
                client_endpoint = f"https://{DOMAIN}/rest/",
                member_id = auth_dict["member_id"],
                application_token = APP_SID,
                placement_options = auth_dict["PLACEMENT_OPTIONS"]
            )
            await insert_auth(session, auth)

            url_bilder = CirculationApplicationUrlBuilder(auth,session)

            log(LogMessage(time=None,heder="Install.", 
                            heder_dict={
                            },
                            body=
                            {
                                "DOMAIN":DOMAIN,
                                "PROTOCOL":PROTOCOL,
                                "LANG":LANG,
                                "APP_SID":APP_SID,
                                "auth_dict":auth_dict
                            },
                            level=log_en.DEBUG))
            
            if event_binds:
                event_arr = []
                for event in event_binds:
                    event_arr.append(
                        {
                            "method": "event.bind",
                            "params":{
                                "event": event.event,
                                "handler": settings.APP_HENDLER_ADDRESS+event.handler
                            }
                        }
                    )
                await call_batch(url_bilder, event_arr)

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


    @router.post("/index")
    async def index_post(DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str, request: Request, session: AsyncSession = Depends(get_session)):
        auth_dict = decode_auth(str(await request.body()))

        log(LogMessage(time=None,heder="Init.", 
                    heder_dict={
                    },
                    body=
                    {
                        "DOMAIN":DOMAIN,
                        "PROTOCOL":PROTOCOL,
                        "LANG":LANG,
                        "APP_SID":APP_SID,
                        "auth_dict":auth_dict
                    },
                    level=log_en.DEBUG))

        auth = await get_auth_by_member_id(session=session, member_id=auth_dict["member_id"])
        url_bilder = CirculationApplicationUrlBuilder(auth,session)

        res = await call_method(url_bilder,"crm.contact.add",
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

        res1 = await call_batch(
            url_bilder,
            [
                {
                    "method": "crm.contact.add",
                    "params":{
                        "FIELDS":{
                            "NAME":"Иван1",
                            "LAST_NAME":"Петров1"
                        }
                    }
                },
                {
                    "method": "crm.contact.add",
                    "params":{
                        "FIELDS":{
                            "NAME":"Иван2",
                            "LAST_NAME":"Петров2"
                        }
                    }
                }
            ])

        arr = []
        for i in range(46):
            arr.append(
                {
                    "method": "crm.contact.add",
                    "params":{
                        "FIELDS":{
                            "NAME":f"Иван{i}",
                            "LAST_NAME":f"Петров{i}"
                        }
                    }
                }
            )

        arr.insert(10,
                {
                    "method": "crm.contact.add",
                    "params":{
                        "FIELDS":"NAME"
                    }
                }
            )
        res2 = await call_batch(url_bilder, arr, True)

        res3 = await get_list(url_bilder, "crm.contact.list")

        return {"res":res, "res1":res1, "res2":res2, "res3": res3}

    app.include_router(router, tags=["webhook"])

    return app
