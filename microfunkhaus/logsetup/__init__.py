import logging
import threading
from datetime import datetime as dt
root_logger_name = 'chrdio'
import json


with open("logsetup.json", 'r') as f:
    d = json.load(f)
LOG_LEVEL = d["logging_level"]


def get_logger(name, root=root_logger_name):
    logger = logging.getLogger(f'{root}.{name}')
    logger.setLevel(LOG_LEVEL)
    
    name_prefix = dt.now().strftime('%Y-%m-%d %H:%M')+f" {threading.get_ident()}"
    file_handler = logging.FileHandler(f'{name_prefix}-unified.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    ff = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(ff)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    sf = logging.Formatter('%(levelname)s:%(name)s - %(message)s')
    stream_handler.setFormatter(sf)
    logger.addHandler(stream_handler)
    return logger