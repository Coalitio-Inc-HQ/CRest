class Auth():
    """
    Абстракный класс аутентификации.
    """

    def bild_url(self, method: str, params_str: str) -> str:
        """
        Собирает url для вызова метода.
        """
        pass


    @property
    def domain(self) -> str:
        """
        Получает домен портала.
        """
        pass
    

    @property
    async def member_id(self) -> str | None:
        """
        Получает id портала.
        """
        pass
    

    @property
    async def user_id(self) -> str:
        """
        Получает id пользователя.
        """
        pass
    
    
    @property
    async def is_admin(self) -> bool:
        """
        Проверяет является ли пользователь адменистратором.
        """
        pass


class AuthFrame(Auth):
    def __init__(self, DOMAIN: str, AUTH_ID: str, AUTH_EXPIRES: int, REFRESH_ID: str, MEMBER_ID: str) -> None:
        self.DOMAIN = DOMAIN
        self.AUTH_ID = AUTH_ID
        self.AUTH_EXPIRES = AUTH_EXPIRES
        self.REFRESH_ID = REFRESH_ID
        self.MEMBER_ID = MEMBER_ID
        super().__init__()
    
    
    def bild_url(self, method: str, params_str: str) -> str:
        """
        Собирает url для вызова метода.
        """
        return f"https://{self.DOMAIN}/rest/{method}.json"+"?"+params_str+"&auth="+self.auth.access_token
    
    @property
    def domain(self) -> str:
        """
        Получает домен портала.
        """
        return self.DOMAIN
    

    # @property
    # async def member_id(self) -> str | None:
    #     """
    #     Получает id портала.
    #     """
    #     pass
    

    # @property
    # async def user_id(self) -> str:
    #     """
    #     Получает id пользователя.
    #     """
    #     pass



class AuthOAuth2(Auth):
    pass

class AuthEvent(Auth):
    access_token:str
    expires: int
    expires_in: int
    scope: str
    domain: str
    server_endpoint: str
    status: str
    client_endpoint: str
    member_id: str
    user_id: str
    application_token:str


class AuthDataBase(Auth):
    pass

class AuthWebHook(Auth):
    pass