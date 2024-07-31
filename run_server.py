import uvicorn
from src.app import build_app
from src.settings import settings
from src.call.сall_parameters_decoder.сall_parameters_decoder import decode_body_request

from src.event_bind import EventBind

from src.placement_bind import PlacementBind

from fastapi import FastAPI, Body, APIRouter,Request,Depends

from fastapi.responses import HTMLResponse

# import src.check_server # не убирать

router = APIRouter()

@router.post("/onCrmContactAdd")
async def onCrmContactAdd(params: dict | None = Depends(decode_body_request)):
    print(params)


@router.post("/LEFT_MENU", response_class=HTMLResponse)
async def onCrmContactAdd(params: dict | None = Depends(decode_body_request)):
    return """
    <body>
        welcome!
    </body>
    """

app = build_app(
    routers=[router],
    event_binds=[EventBind("onCrmContactAdd", "/onCrmContactAdd")],
    placement_binds= [PlacementBind("welcome!", "LEFT_MENU", "/LEFT_MENU")]
    )

uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)

# можно ли открыто хранить токены в бд?
# индентифицировать ли отдельного пользователя?