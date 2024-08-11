from src.database.schemes import AuthDTO
from src.settings import settings
from src.database.database_requests import *
from .url_builder import UrlBuilder


class FrameUrlBuilder(UrlBuilder):
    def __init__(self, auth: AuthDTO):
        super().__init__(True, True)
        self.auth = auth
    

    def build_url (self, method:str, params: str) -> str:
        return f"https://{self.auth.domain}/rest/{method}.{self.strategy}"+"?"+params+"&auth="+self.auth.access_token


    async def update_auth(self) -> None:
        new_auth = await self.refresh_auth(
            {
            "client_id": settings.C_REST_CLIENT_ID,
            "grant_type": "refresh_token",
            "client_secret": settings.C_REST_CLIENT_SECRET,
            "refresh_token": self.auth.refresh_token
            }
        )
        
        self.auth.access_token = new_auth["access_token"],
        self.auth.expires = int(new_auth["expires"]),
        self.auth.expires_in = int(new_auth["expires_in"]),
        self.auth.scope = new_auth["scope"],
        self.auth.domain = new_auth["domain"],
        self.auth.status = new_auth["status"],
        self.auth.member_id = new_auth["member_id"],
        self.auth.user_id = int(new_auth["user_id"]),
        self.auth.refresh_token = new_auth["refresh_token"],



    async def update_domain(self, domain: str) -> None:
        self.auth.client_endpoint = domain

    def get_name(self) -> str:
        return self.auth.member_id
