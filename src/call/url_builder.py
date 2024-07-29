from src.database.schemes import AuthDTO
from src.settings import settings
from src.database.database_requests import *

class UrlBuilder:
    """
    Абстрацный класс сборщика url
    """
    def __init__(self, is_reauth: bool, is_redomain: bool) -> None:
        self.strategy = "json"
        self.is_reauth = is_reauth
        self.is_redomain = is_redomain


    def build_url(self, method:str, params: str) -> str:
        pass

    
    def build_url_update_auth(self) -> str:
        pass


    async def update_auth(self, access_token: str, expires_in: int, client_endpoint: str, refresh_token: str) -> None:
        pass


    async def update_domain(self, domain: str) -> None:
        pass


class WebHookUrlBuilder(UrlBuilder):
    def __init__(self) -> None:
        super().__init__(False, False)


    def build_url (self, method:str, params: str) -> str:
        return f"{settings.C_REST_WEB_HOOK_URL}/{method}.{self.strategy}"+"?"+params
    

class CirculationApplicationUrlBuilder(UrlBuilder):
    def __init__(self, auth: AuthDTO, session: AsyncSession) -> None:
        super().__init__(True, True)
        self.auth = auth
        self.session = session
    

    def build_url (self, method:str, params: str) -> str:
        return f"{self.auth.client_endpoint}{method}.{self.strategy}"+"?"+params+"&auth="+self.auth.access_token


    def build_url_update_auth(self) -> str:
        return f"https://oauth.bitrix.info/oauth/token/?client_id={settings.C_REST_CLIENT_ID}&grant_type=refresh_token&client_secret={settings.C_REST_CLIENT_SECRET}&refresh_token={self.auth.refresh_token}"


    async def update_auth(self, access_token: str, expires_in: int, client_endpoint: str, refresh_token: str) -> None:
        await update_auth(self.session, self.auth.member_id, access_token, expires_in, client_endpoint, refresh_token)
        self.auth.access_token = access_token
        self.auth.expires_in = expires_in
        self.auth.client_endpoint = client_endpoint
        self.auth.refresh_token = refresh_token


    async def update_domain(self, domain: str) -> None:
        await update_auth_domain(self.session, self.auth.member_id, domain)
        self.auth.client_endpoint = domain


web_hook_url_builder = WebHookUrlBuilder()