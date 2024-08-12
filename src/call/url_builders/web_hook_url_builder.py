from .url_builder import UrlBuilder
from src.settings import settings

class WebHookUrlBuilder(UrlBuilder):
    def __init__(self):
        super().__init__(False, False)


    def build_url (self, method:str, params: str) -> str:
        return f"{settings.C_REST_WEB_HOOK_URL}/{method}.{self.strategy}"+"?"+params
    
    
    def get_name(self) -> str:
        return settings.C_REST_WEB_HOOK_URL


async def get_web_hook_url_builder_depends():
    def get_url_builder() -> UrlBuilder:
        return WebHookUrlBuilder()
    return get_url_builder


async def get_web_hook_url_builder_init_depends():
    def get_init_url_builder() -> UrlBuilder:
        return WebHookUrlBuilder()
    return get_init_url_builder
