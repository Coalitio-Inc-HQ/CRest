from CRest.database.schemes import AuthDTO
from CRest.settings import settings
from CRest.database.database_requests import *
from ..url_builder import UrlBuilder
from .base_url_builder import BaseUrlBuilder

from fastapi import Depends, Request

from CRest.call.сall_parameters_decoder.сall_parameters_decoder import get_body


class LocalApplicationUrlBuilder(BaseUrlBuilder):
    def __init__(self, filename: str):
        super().__init__(True, True)
        self.filename=filename

        with open(filename) as json_data:
            self.auth = AuthDTO.model_validate_json(json_data.read())
    

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
        
        self.auth.access_token = new_auth["access_token"]
        self.auth.expires = int(new_auth["expires"])
        self.auth.expires_in = int(new_auth["expires_in"])
        self.auth.scope = new_auth["scope"]
        self.auth.domain = new_auth["client_endpoint"][8:-6]
        self.auth.status = new_auth["status"]
        self.auth.member_id = new_auth["member_id"]
        self.auth.user_id = int(new_auth["user_id"])
        self.auth.refresh_token = new_auth["refresh_token"]
    
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(self.auth.model_dump_json())



    async def update_domain(self, domain: str) -> None:
        self.auth.domain = domain

        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(self.auth.model_dump_json())

    def get_name(self) -> str:
        return self.auth.member_id
    
    async def set_settings(self, settings: dict) -> None:
        self.auth.settings = settings

        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(self.auth.model_dump_json())

    def get_settings(self) -> dict:
        return self.auth.settings


def get_local_application_url_builder_depends(filename: str):
    def get_url_builder() -> UrlBuilder:
        return LocalApplicationUrlBuilder(filename)
    return get_url_builder


def get_local_application_url_builder_init_depends(filename: str):
    def get_init_url_builder(request: Request , body: dict | None = Depends(get_body)) -> UrlBuilder:
        
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

                settings={}
            )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(auth.model_dump_json())
        return LocalApplicationUrlBuilder(filename)
    
    return get_init_url_builder
