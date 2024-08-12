from pydantic import BaseModel
from enum import Enum
from typing import Any

class log_en (Enum):
    INFO = "info"
    ERROR = "error"
    DEBUG = "debug"


class LogMessage (BaseModel):
    time: str | None
    level: log_en
    header: str 
    header_dict: Any | None
    body: Any | None

