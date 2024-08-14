from pydantic import BaseModel
from enum import Enum
from typing import Any

import uuid


class log_en (Enum):
    """
    Уровни из logging.
    """
    INFO = "info"
    ERROR = "error"
    DEBUG = "debug"


class LogHeader(BaseModel):
    """
    Заголовок сообщения логов.

    id      - Идентификатор сообщения;
    title   - Заголовок сообщения;
    tegs    - Теги сообщения, предназначены для фильтрации;
    time    - Время создания сообщения;
    level   - Важность сообщения.
    """
    id: uuid.UUID
    title: str
    tegs: dict
    time: str | None
    level: log_en


class LogMessage(BaseModel):
    """
    Сообщение лога.

    header  - Заголовок сообщения;
    body    - Тело сообщения.
    """
    header: LogHeader
    body: Any | None
