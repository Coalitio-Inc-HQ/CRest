import logging
from src.loging.logger import json_logger
from .schemes import LogMessage, log_en
import datetime

cmd_logger = logging.getLogger(__name__)


def log_info(messege: LogMessage):
    cmd_logger.info(f"INFO: {messege.heder}")

    cmd_logger.info(messege.model_dump_json())

    json_logger.info(messege.model_dump_json())


def log_error(messege: LogMessage):
    cmd_logger.error(f"ERROR: {messege.heder}")

    cmd_logger.error(messege.model_dump_json())

    json_logger.error(messege.model_dump_json())


def log_debug(messege: LogMessage):
    cmd_logger.debug(f"DEBUG: {messege.heder}")

    cmd_logger.debug(messege.model_dump_json())

    json_logger.debug(messege.model_dump_json())


log_swith = {
    log_en.INFO: log_info,
    log_en.ERROR: log_error,
    log_en.DEBUG: log_debug,
}


def log(messege: LogMessage):
    messege.time = datetime.datetime.now().isoformat()
    log_swith[messege.level](messege)

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