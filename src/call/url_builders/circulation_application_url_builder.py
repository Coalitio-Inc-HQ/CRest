from src.database.schemes import AuthDTO
from src.settings import settings
from src.database.database_requests import *
from .url_builder import UrlBuilder
from fastapi import Depends, Request
from src.call.сall_parameters_decoder.сall_parameters_decoder import get_body

from src.database.database_requests import insert_auth

class CirculationApplicationUrlBuilder(UrlBuilder):
    def __init__(self, auth: AuthDTO, session: AsyncSession):
        super().__init__(True, True)
        self.auth = auth
        self.session = session
    

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

        await update_auth(self.session, 
                        new_auth["access_token"],
                        int (new_auth["expires"]),
                        int(new_auth["expires_in"]),
                        new_auth["scope"],
                        new_auth["client_endpoint"][8:-6],
                        new_auth["status"],
                        new_auth["member_id"],
                        int(new_auth["user_id"]),
                        new_auth["refresh_token"],
                        )
        
        self.auth.access_token = new_auth["access_token"]
        self.auth.expires = int(new_auth["expires"])
        self.auth.expires_in = int(new_auth["expires_in"])
        self.auth.scope = new_auth["scope"]
        self.auth.domain = new_auth["client_endpoint"][8:-6]
        self.auth.status = new_auth["status"]
        self.auth.member_id = new_auth["member_id"]
        self.auth.user_id = int(new_auth["user_id"])
        self.auth.refresh_token = new_auth["refresh_token"]



    async def update_domain(self, domain: str) -> None:
        await update_auth_domain(self.session, self.auth.member_id, domain)
        self.auth.client_endpoint = domain

    def get_name(self) -> str:
        return self.auth.member_id

def get_circulation_application_url_builder_depends(get_session):
    async def get_url_builder(session: AsyncSession = Depends(get_session), body: dict | None = Depends(get_body)) -> UrlBuilder:
        member_id = None
        if "member_id" in body:
            member_id=body["member_id"]
        elif "auth" in body:
            if "member_id" in body["auth"]:
                member_id = body["auth"]["member_id"]

        auth = await get_auth_by_member_id(session=session, member_id=member_id)
        return CirculationApplicationUrlBuilder(auth, session)
    return get_url_builder


def get_circulation_application_url_builder_init_depends(get_session):
    async def get_init_url_builder(request: Request , body: dict | None = Depends(get_body), session: AsyncSession = Depends(get_session)) -> UrlBuilder:
        
        params = request.query_params._dict

        auth = AuthDTO(
                lang=params["LANG"],
                app_id=params["APP_SID"],

                access_token = body["AUTH_ID"],
                expires=None,
                expires_in = int(body["AUTH_EXPIRES"]),
                scope=None,
                domain=params["DOMAIN"],
                status= body ["status"],
                member_id = body["member_id"],
                user_id=None,
                refresh_token = body["REFRESH_ID"],
            )

        await insert_auth(session, auth)
        return CirculationApplicationUrlBuilder(auth,session)
            
    
    return get_init_url_builder
