from CRest.call.url_builders.url_builder import UrlBuilder

class EventLoopBreakerBase():
    async def chek_event(self, url_builder: UrlBuilder, event: str, values: dict) -> bool:
        """
        Проверяет произощёл ли повторынй вызов события.

        Результат:
        True - событие ренне не встречалось;
        False - событие встретилось ранее.
        """
        pass

    async def register_event(self, url_builder: UrlBuilder, event: str, values: dict) -> None:
        """
        Регестирует событие.
        """
        pass