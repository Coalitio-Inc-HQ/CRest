from pydantic import BaseModel, Field
from datetime import datetime


class AuthDTO(BaseModel):
    AUTH_ID: str
    AUTH_EXPIRES: int
    REFRESH_ID: str
    member_id: str
    status: str
    PLACEMENT: str
    PLACEMENT_OPTIONS: dict

