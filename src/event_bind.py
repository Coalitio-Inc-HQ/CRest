from fastapi import APIRouter

class EventBind:
    def __init__(self,event: str, handler: str, hendler_router: APIRouter) -> None:
        self.event = event
        self.handler = handler
        self.hendler_router = hendler_router
