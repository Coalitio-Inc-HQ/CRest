from pydantic import BaseModel, Field
from datetime import datetime


class AuthDTO(BaseModel):
    """
    lang: str
    app_id: str

    access_token: str
    expires: int | None
    expires_in: int
    scope: str | None
    domain: str
    status: str
    member_id: str | None
    user_id: int | None
    refresh_token: str
    """
    lang: str | None
    app_id: str | None

    access_token: str
    expires: int | None
    expires_in: int
    scope: str | None
    domain: str
    status: str
    member_id: str | None
    user_id: int | None
    refresh_token: str | None
