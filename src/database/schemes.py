from pydantic import BaseModel, Field
from datetime import datetime


class AuthDTO(BaseModel):
    """
    access_token: str
    expires_in: int
    refresh_token: str
    client_endpoint: str
    member_id: str
    application_token: str | None
    placement_options: dict | None
    """
    access_token: str
    expires_in: int
    refresh_token: str
    client_endpoint: str
    member_id: str
    application_token: str | None
    placement_options: dict | None

    # AUTH_ID: str
    # AUTH_EXPIRES: int
    # REFRESH_ID: str
    # member_id: str
    # status: str
    # PLACEMENT: str
    # PLACEMENT_OPTIONS: dict

