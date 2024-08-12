from src.database.schemes import AuthDTO
from src.settings import settings
from src.database.database_requests import *
from .url_builder import UrlBuilder


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
