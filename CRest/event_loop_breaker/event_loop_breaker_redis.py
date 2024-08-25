from CRest.event_loop_breaker.event_loop_breaker_base import EventLoopBreakerBase
from CRest.call.url_builders.url_builder import UrlBuilder

import json

import redis.asyncio as redis

class EventLoopBreakerRedis(EventLoopBreakerBase):
    def __init__(self, url: str, password: str = None, ex: int = 60) -> None:
        super().__init__()
        if password:
            self.pool = redis.ConnectionPool.from_url(url+f"?decode_responses=True&password={password}")
        else:
            self.pool = redis.ConnectionPool.from_url(url+"?decode_responses=True")
        self.ex = ex

    async def chek_event(self, url_builder: UrlBuilder, event: str, values: dict) -> bool:
        """
        Проверяет произощёл ли повторынй вызов события.

        Результат:
        True - событие ренне не встречалось;
        False - событие встретилось ранее.
        """
        async with redis.Redis.from_pool(self.pool) as conn:
            res = await conn.get(url_builder.get_name()+event)

            if not res:
                return True

            res_dict = json.loads(res)

            return not values == res_dict
        

    async def register_event(self, url_builder: UrlBuilder, event: str, values: dict) -> None:
        """
        Регестирует событие.
        """
        async with redis.Redis.from_pool(self.pool) as conn:
            await conn.set(url_builder.get_name()+event, json.dumps(values), ex=self.ex)