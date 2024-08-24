from CRest.database.schemes import AuthDTO
from CRest.settings import settings
from CRest.database.database_requests import *
from .url_builder import UrlBuilder

from fastapi import Depends
from CRest.call.сall_parameters_decoder.сall_parameters_decoder import get_body

class EventUrlBuilder(UrlBuilder):
    def __init__(self, auth: AuthDTO):
        super().__init__(False, True)
        self.auth = auth
    

    def build_url (self, method:str, params: str) -> str:
        return f"https://{self.auth.domain}/rest/{method}.{self.strategy}"+"?"+params+"&auth="+self.auth.access_token


    async def update_domain(self, domain: str) -> None:
        self.auth.domain = domain

    def get_name(self) -> str:
        return self.auth.member_id


def get_event_url_builder_depends(body: dict | None = Depends(get_body)) -> UrlBuilder:
    auth = AuthDTO(
                lang=None,
                app_id=body["auth"]["application_token"],

                access_token = body["auth"]["access_token"],
                expires=int(body["auth"]["expires"]),
                expires_in = int(body["auth"]["expires_in"]),
                scope=body["auth"]["scope"],
                domain=body["auth"]["domain"],
                status= body["auth"]["status"],
                member_id = body["auth"]["member_id"],
                user_id=body["auth"]["user_id"],
                refresh_token = None,

                settings= None
            )
    
    return EventUrlBuilder(auth)
