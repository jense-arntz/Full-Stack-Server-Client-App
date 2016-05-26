import logging
from logging.handlers import *
PROGID = 'CeeClient'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
LOG_FILE = '/tmp/Client_APP.log'
LOG_SYSFILE = '/var/log/everything.log'


def get_memory_log_handler():

    handler = logging.FileHandler(LOG_FILE)
    handler.name = 'in-memory log'
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return handler





