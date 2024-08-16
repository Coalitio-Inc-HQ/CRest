from pydantic import BaseModel

class PlacementBind(BaseModel):
    title: str
    placement: str
    handler: str
