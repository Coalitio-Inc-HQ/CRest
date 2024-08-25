from CRest.event_loop_breaker.event_loop_breaker_redis import EventLoopBreakerRedis

from CRest.call.url_builders.base_url_builders.web_hook_url_builder import WebHookUrlBuilder

b = EventLoopBreakerRedis("redis://localhost")

import asyncio 

async def s():
    # await b.register_event(WebHookUrlBuilder("conf.json"), "asd", {"key":"value"})
    print(await b.chek_event(WebHookUrlBuilder("conf.json"), "asd", {"key":"value"}))


asyncio.run(s())