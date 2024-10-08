import uvicorn
from src.app import BitrixAPI, BitrixAPIMode
from src.settings import settings
from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request
from fastapi import Depends

from fastapi.responses import HTMLResponse

from src.call.url_builders.frame_url_builder import FrameUrlBuilder, get_frame_url_builder_depends
from src.call.url_builders.event_url_builder import EventUrlBuilder, get_event_url_builder_depends


from src.call.сall_parameters_decoder.сall_parameters_decoder import get_body


from src.call.calls import CallAPIBitrix

from src.call.call_director import CallDirectorBarrelStrategy
from src.call.url_builders.oauth2_url_builder import get_oauth_2_url_builder_depends

# import src.check_server # не убирать


app = BitrixAPI(
    BitrixAPIMode.CirculationApplication,
    CallAPIBitrix(CallDirectorBarrelStrategy()),
)


@app.head("/install")
async def init_head():
    pass


@app.head("/index")
async def index_head():
    pass


@app.post("/install", response_class=HTMLResponse)
async def install_post(url_builder=Depends(app.url_bulder_init_depends), body: dict | None = Depends(get_body)):
    url_builder = url_builder

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


@app.get("/index")
async def index_get(url_builder=Depends(get_oauth_2_url_builder_depends)):

    res = await app.call_api_bitrix.call_method(url_builder, "crm.contact.add",
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


@app.post("/index")
async def index_post(url_builder=Depends(app.url_bulder_depends),):

    res = await app.call_api_bitrix.call_method(url_builder, "crm.contact.add",
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

    res1 = await app.call_api_bitrix.call_batch(
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
    res2 = await app.call_api_bitrix.call_batch(url_builder, arr, True)

    return {"res": res, "res1": res1, "res2": res2}


@app.add_event_bind("onCrmContactAdd")
async def onCrmContactAdd(url_builder=Depends(get_event_url_builder_depends)):
    res = await app.call_api_bitrix.call_method(url_builder, "crm.contact.add",
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

    return res


@app.add_placement_bind("LEFT_MENU", "HI")
async def LEFT_MENU(url_builder=Depends(get_frame_url_builder_depends)):

    res = await app.call_api_bitrix.call_method(url_builder, "crm.contact.add",
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
    return res


@app.add_placement_bind("CRM_DEAL_DETAIL_ACTIVITY", "DEAL", response_class=HTMLResponse)
async def CRM_DEAL_DETAIL_ACTIVITY(url_builder=Depends(get_frame_url_builder_depends)):
    return """
    CRM_DEAL_DETAIL_ACTIVITY
    """


@app.post("/settings")
async def settings1(params: dict | None = Depends(decode_body_request)):
    return params


@app.add_event_bind("onAppInstall")
async def onAppInstall(url_builder=Depends(get_event_url_builder_depends)):
    return "ok"

uvicorn.run(app.app, host=settings.APP_HOST, port=settings.APP_PORT)
