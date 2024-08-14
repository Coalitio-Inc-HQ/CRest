from ..url_builder import  UrlBuilder

class BaseUrlBuilder(UrlBuilder):
    def __init__(self, is_reauth: bool, is_redomain: bool):
        super.__init__(is_reauth, is_redomain)

    def get_settings(self) -> dict:
        pass
