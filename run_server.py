import uvicorn
from src.app import BitrixAPI, BitrixAPIMode
from src.settings import settings
from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request

from src.event_bind import EventBind

from src.placement_bind import PlacementBind

from fastapi import FastAPI, Body, APIRouter,Request,Depends

from fastapi.responses import HTMLResponse

from src.call.url_builders.frame_url_builder import FrameUrlBuilder, get_frame_url_builder_depends
from src.call.url_builders.event_url_builder import EventUrlBuilder, get_event_url_builder_depends

from src.database.schemes import AuthDTO

from src.call.calls import CallAPIBitrix

from src.call.call_director import CallDirectorBarrelStrategy

# import src.check_server # не убирать

app = BitrixAPI(
    BitrixAPIMode.CirculationApplication,
    CallAPIBitrix(CallDirectorBarrelStrategy()),
    )


@app.add_event_bind("onCrmContactAdd")
async def onCrmContactAdd(url_builder = Depends(get_event_url_builder_depends)):
    res = await app.call_api_bitrix.call_method(url_builder,"crm.contact.add",
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



@app.add_placement_bind("LEFT_MENU","HI")
async def LEFT_MENU(url_builder = Depends(get_frame_url_builder_depends)):

    res = await app.call_api_bitrix.call_method(url_builder,"crm.contact.add",
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

@app.add_placement_bind("CRM_DEAL_DETAIL_ACTIVITY", "DEAL", response_class=HTMLResponse)
async def CRM_DEAL_DETAIL_ACTIVITY(url_builder = Depends(get_frame_url_builder_depends)):
    return """
    CRM_DEAL_DETAIL_ACTIVITY
    """

@app.post("/settings")
async def settings1(params: dict | None = Depends(decode_body_request)):
    return params

@app.add_event_bind("onAppInstall")
async def onAppInstall(url_builder = Depends(get_event_url_builder_depends)):
    return "ok"

uvicorn.run(app.app, host=settings.APP_HOST, port=settings.APP_PORT)

