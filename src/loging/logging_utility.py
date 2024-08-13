import logging
from src.loging.logger import json_logger
from .schemes import LogMessage, log_en
import datetime

cmd_logger = logging.getLogger(__name__)


def log_info(message: LogMessage):
    cmd_logger.info(f"INFO: {message.header}")

    cmd_logger.info(message.model_dump_json())

    json_logger.info(message.model_dump_json())


def log_error(message: LogMessage):
    cmd_logger.error(f"ERROR: {message.header}")

    cmd_logger.error(message.model_dump_json())

    json_logger.error(message.model_dump_json())


def log_debug(message: LogMessage):
    cmd_logger.debug(f"DEBUG: {message.header}")

    cmd_logger.debug(message.model_dump_json())

    json_logger.debug(message.model_dump_json())


log_swith = {
    log_en.INFO: log_info,
    log_en.ERROR: log_error,
    log_en.DEBUG: log_debug,
}


def log(message: LogMessage):
    message.time = datetime.datetime.now().isoformat()
    log_swith[message.level](message)

def filter_array_to_str(arr: list) -> list:
    res = []
    for item in arr:
        if isinstance(item, str):
            res.append(item)
    return res

def filter_dict_to_str(dict: dict):
    res = {}
    for key, item in dict.items():
        if isinstance(item, str):
            res[key] = item
    return res