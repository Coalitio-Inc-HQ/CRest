from pydantic import BaseModel

class EventBind(BaseModel):
    event: str
    handler: str