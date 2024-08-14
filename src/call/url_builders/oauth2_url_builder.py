from src.database.schemes import AuthDTO
from src.settings import settings
from src.database.database_requests import *
from .url_builder import UrlBuilder

from fastapi import Request

class OAuth2UrlBuilder(UrlBuilder):
    """
    Обязательно использовать get_auth
    """
    def __init__(self, code: str):
        super().__init__(True, True)
        self.code = code
        self.auth = None
    
    async def get_auth(self)  -> None:
        new_auth = await self.refresh_auth(
            {
            "client_id": settings.C_REST_CLIENT_ID,
            "grant_type": "authorization_code",
            "client_secret": settings.C_REST_CLIENT_SECRET,
            "code": self.code
            }
        )

        self.auth = AuthDTO(
                            lang=None,
                            app_id=None,

                            access_token = new_auth["access_token"],
                            expires= int(new_auth["expires"]),
                            expires_in = int(new_auth["expires_in"]),
                            scope=new_auth["scope"],
                            domain=new_auth["client_endpoint"][8:-6],
                            status=new_auth["status"],
                            member_id = new_auth["member_id"],
                            user_id=int(new_auth["user_id"]),
                            refresh_token = new_auth["refresh_token"],

                            settings=None
        )


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
        self.auth.domain = domain

    def get_name(self) -> str:
        return self.auth.member_id


async def get_oauth_2_url_builder_depends(request: Request) -> UrlBuilder:
    params = request.query_params._dict
    url_builder = OAuth2UrlBuilder(params["code"])
    await url_builder.get_auth()
    return url_builder
