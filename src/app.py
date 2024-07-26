from fastapi import FastAPI, Body, APIRouter,Request,Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .loging.logging_utility import log, LogMessage,log_en
from .settings import settings
from .utils import decode_auth

from .database.session_database import get_session, AsyncSession
from .database.database_requests import *

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


router = APIRouter()

@app.get("/")
async def root():
    return RedirectResponse("/docs")


@router.head("/init")
async def init_head():
    pass

@router.head("/index")
async def index_head():
    pass

@router.post("/init", response_class=HTMLResponse)
async def init_post (DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str,request: Request, session: AsyncSession = Depends(get_session)):
    auth_dict = decode_auth(str(await request.body()))
    await insert_auth(session, AuthDTO.model_validate(auth_dict,from_attributes=True))

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
            installation has been finished
    </body>
    """


@router.post("/index")
async def index_post(DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str, request: Request):
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

app.include_router(router, tags=["webhook"])
