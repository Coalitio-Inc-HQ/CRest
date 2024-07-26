from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """
    Класс отвечает за чтение настроек сервера и CRest.
    """

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_ECHO: bool

    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_USER_TEST: str
    DB_PASS_TEST: str
    DB_NAME_TEST: str

    APP_HOST: str
    APP_PORT: int
    BACKEND_CORS_ORIGINS: str

    LOG_PATH:str

    C_REST_WEB_HOOK_URL:str

    C_REST_CLIENT_ID:str
    C_REST_CLIENT_SECRET:str
    

    BATCH_COUNT: int


    @property
    def DATABASE_URL_ASINC(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def BACKEND_CORS_ORIGINS(self):
        return self.BACKEND_CORS_ORIGINS.split(",")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def get_app_settings():
    """
    Формирует настройки CRest.
    """

    if (settings.C_REST_WEB_HOOK_URL!=""):
        return {
            "is_web_hook": True,
            "C_REST_WEB_HOOK_URL": settings.C_REST_WEB_HOOK_URL
        }
    
    # дописать про Application

def get_url(method:str):
    settings = get_app_settings()
    
    url=""
    if settings["is_web_hook"]:
        url=f"{settings["C_REST_WEB_HOOK_URL"]}/{method}.json"
    else:
        pass # дописать про Application