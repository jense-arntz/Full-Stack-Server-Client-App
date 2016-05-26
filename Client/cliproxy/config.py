import ConfigParser
import sqlite3 as sqlite
from uuid import getnode as get_mac
from logger import *


def get_device_id():
    mac = ''.join('%012x' % get_mac())
    return mac


def get_server_addr(db_name):
    addr = ""
    if os.path.exists(db_name):
        con = sqlite.connect(db_name)
        cur = con.cursor()
        result = cur.execute("select server_addr from IP")
        addr = result.fetchone()
        con.close()
    else:
        logger.error('cannot found database: %s', db_name)

    return addr


def config_section_map(config, section):
    d = {}
    options = config.options(section)
    for option in options:
        try:
            d[option] = config.get(section, option)
            if d[option] == -1:
                logger.debug('error')
        except:
            logger.error("exceptions on %s" % option)
            d[option] = None

    return d


def load_config():
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ceeproxy.conf')

    config.read(config_path)

    api_key = config_section_map(config=config, section="SERVER")["api_key"]

    # server_addr = config_section_map(config=config, sect
    # ion="SERVER")["addr"]
    db_name = config_section_map(config=config, section="DATABASE")["db_name"]
    server_addr = get_server_addr(db_name)
    logger.debug(server_addr)
    # device_id = config_section_map(config=config, section="DEVICE")["mac"]
    device_id = get_device_id()
    logger.debug(device_id)
    if server_addr is not None:
        SERVER_ADDR = server_addr[0]
        logger.debug("before: %s" % SERVER_ADDR)
    if api_key is not None:
        SERVER_API_KEY = api_key
    if device_id is not None:
        DEVICE_ID = device_id
        logger.debug("before: %s" % DEVICE_ID)

    logger.debug('server address: %s', SERVER_ADDR)
    logger.debug('server api key: %s', SERVER_API_KEY)
    logger.debug('device id: %s', DEVICE_ID)

    return [SERVER_ADDR, SERVER_API_KEY, DEVICE_ID]
