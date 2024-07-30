import uvicorn
from src.app import build_app
from src.settings import settings
from src.call.сall_parameters_decoder import decode_body_request

from src.event_bind import EventBind

from fastapi import FastAPI, Body, APIRouter,Request,Depends

# import src.check_server # не убирать

router = APIRouter()

@router.post("/onCrmContactAdd")
async def onCrmContactAdd(params: dict | None = Depends(decode_body_request)):
    print(params)


app = build_app(event_binds=[EventBind("onCrmContactAdd", "/onCrmContactAdd", router)])

uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)

# можно ли открыто хранить токены в бд?
# индентифицировать ли отдельного пользователя?