import uvicorn
from src.app import BitrixAPI, BitrixAPIMode
from src.settings import settings
from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request

from src.event_bind import EventBind

from src.placement_bind import PlacementBind

from fastapi import FastAPI, Body, APIRouter,Request,Depends

from fastapi.responses import HTMLResponse

# from src.call.url_builders.web_hook_url_builder import get_web_hook_url_builder
from src.call.url_builders.frame_url_builder import FrameUrlBuilder
from src.call.url_builders.event_url_builder import EventUrlBuilder

from src.database.schemes import AuthDTO

from src.call.calls import CallAPIBitrix

from src.call.call_director import CallDirectorBarrelStrategy

# import src.check_server # не убирать

router = APIRouter()

@router.post("/onCrmContactAdd")
async def onCrmContactAdd(body: dict | None = Depends(decode_body_request)):
    auth = AuthDTO(
                lang=None,
                app_id=body["auth"]["application_token"],

                access_token = body["auth"]["access_token"],
                expires=int(body["auth"]["expires"]),
                expires_in = int(body["auth"]["expires_in"]),
                scope=body["auth"]["scope"],
                domain=body["auth"]["domain"],
                status= body["auth"]["status"],
                member_id = body["auth"]["member_id"],
                user_id=body["auth"]["user_id"],
                refresh_token = None,
            )
    
    url_builder = EventUrlBuilder(auth)
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

    return res



@router.post("/LEFT_MENU")
async def onCrmContactAdd(DOMAIN:str, PROTOCOL:int, LANG:str, APP_SID:str, body: dict | None = Depends(decode_body_request)):
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
    
    url_builder = FrameUrlBuilder(auth)
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

    return res

@router.post("/CRM_LEAD_DETAIL_ACTIVITY	")
async def onCrmContactAdd(params: dict | None = Depends(decode_body_request)):

    return params

@router.post("/settings")
async def onCrmContactAdd(params: dict | None = Depends(decode_body_request)):
    return params

@router.post("/onAppInstall")
async def onCrmContactAdd(params: dict | None = Depends(decode_body_request)):
    return params


app = BitrixAPI(
    BitrixAPIMode.CirculationApplication,
    routers=[router],
    event_binds=[EventBind("onCrmContactAdd", "/onCrmContactAdd"),
                 EventBind("onAppInstall", "/onAppInstall")
                 ],
    placement_binds= [PlacementBind("welcome!", "LEFT_MENU", "/LEFT_MENU"),
                      PlacementBind("settings", "LANDING_SETTINGS", "/settings"),
                      PlacementBind("CRM_LEAD_DETAIL_ACTIVITY", "CRM_LEAD_DETAIL_ACTIVITY", "/CRM_LEAD_DETAIL_ACTIVITY")
                      ]
    ).app

uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)

# можно ли открыто хранить токены в бд?
# индентифицировать ли отдельного пользователя?