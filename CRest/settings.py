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
    RETURN_LIST_COUNT: int

    OPERATING_MAX_TIME: int

    APP_HANDLER_ADDRESS:str

    IS_CIRCULATION_APP: bool

    @property
    def DATABASE_URL_ASINC(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def BACKEND_CORS_ORIGINS(self):
        return self.BACKEND_CORS_ORIGINS.split(",")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

