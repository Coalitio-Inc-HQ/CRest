from ..url_builder import UrlBuilder
from .base_url_builder import BaseUrlBuilder
from src.settings import settings

import json

class WebHookUrlBuilder(BaseUrlBuilder):
    def __init__(self, filename: str):
        super().__init__(False, False)
        self.filename=filename

        try:
            with open(filename) as json_data:
                self.settings = json.loads(json_data.read())
        except:
            self.settings = {}


    def build_url (self, method:str, params: str) -> str:
        return f"{settings.C_REST_WEB_HOOK_URL}/{method}.{self.strategy}"+"?"+params
    
    
    def get_name(self) -> str:
        return settings.C_REST_WEB_HOOK_URL

    def get_settings(self) -> dict:
        return self.settings


def get_web_hook_url_builder_depends(filename: str):
    def get_url_builder() -> UrlBuilder:
        return WebHookUrlBuilder(filename)
    return get_url_builder


def get_web_hook_url_builder_init_depends(filename: str):
    def get_init_url_builder() -> UrlBuilder:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps({}))
        return WebHookUrlBuilder(filename)
    return get_init_url_builder
