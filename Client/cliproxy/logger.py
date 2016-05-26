from const import *
from logging.handlers import *

logger = logging.getLogger()


def get_stream_handler():
    """Return console logging handler."""
    # Use stderr (default)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    return handler


def get_syslog_handler():
    """Return syslog logging handler."""
    handler = logging.handlers.SysLogHandler("/dev/log",
                                             facility=logging.handlers.SysLogHandler.LOG_LOCAL0)
    formatter = logging.Formatter(
        PROGID + "[%(process)d] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    return handler


def get_memory_log_handler():

    handler = logging.FileHandler(LOG_FILE, mode='w')
    handler.name = 'in-memory log'
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s')
    handler.setFormatter(formatter)
    return handler


def close_memory_log_handler():
    logger = logging.getLogger()
    handlers = logger.handlers[:]
    for handler in handlers:
        if handler.name == 'in-memory log':
            logger.removeHandler(handler)
            handler.flush()
            handler.close()
            break


def open_memory_log_handler():
    logger = logging.getLogger()
    handler = get_memory_log_handler()
    logger.addHandler(handler)


def set_loggers(level=logging.INFO, quiet=True):
    logger = logging.getLogger()
    logger.setLevel(level)

    try:
        # handler = get_syslog_handler()
        # logger.addHandler(handler)

        handler = get_memory_log_handler()
        logger.addHandler(handler)
    except Exception as e:
        print e
