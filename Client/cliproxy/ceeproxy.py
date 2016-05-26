#!/usr/bin/python
"""
https://pypi.python.org/pypi/python-daemon/
http://web.archive.org/web/20131017130434/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

client API

The api should allow for the configuration of the device camera settings and allow for
image capture, and to get system summary information for ip address, ip settings, etc

Proposed API structure:

/api/imgcap/single                          --- return single image
/api/imgcap/hdr3                            --- return HDR3 tar,g archive
/api/imgcap/hdr5                            --- return HDR5 tar,g archive

/api/control/summary                        --- return gphoto2 summary
/api/contorl/[configfField]                 --- return [configValue] for that [configField]
/api/control/[configfField]/[configValue]   --- set [configValue] for that [configField]

/api/sys/summary                            --- get system summary
/api/sys/status                             --- get system status or fault code


server API

proxy API url

/api/client/pull
{
    "token": "123454",
    "timestamp": "123454",
    "deviceid": "deviceid",
    "api": "/api/imgcap/single",
}

/api/client/push
{
    "token": "123454",
    "timestamp": "123454",
    "response": {

    }
}


"""

import requests
import httplib
import Queue as queue
import thread
import threading
import json
import daemon
from time import sleep

from usb import *
from config import *
from utils import *

# DEVICE_ID = ""

# SERVER_API_KEY = ""
SERVER_PORT = 80

SERVER_TOKEN_LEN = 10

CLIENT_ADDR = "127.0.0.1"
CLIENT_PORT = 80

CLIENT_API_URLS = [
    "/api/empty",
    "/api/imgcap/single",
    "/api/imgcap/hdr3",
    "/api/imgcap/hdr5",

    "/api/control/summary",
    "/api/control/[configfField]",
    "/api/control/[configfField]/[configValue]",

    "/api/sys/summary",
    "/api/sys/status",
]

DB_NAME = "Client.db"
logging.getLogger("requests").setLevel(logging.WARNING)


class CeeProxy(object):

    server_addr = ""
    server_port = SERVER_PORT
    client_addr = ""
    client_port = CLIENT_PORT
    device_id = ""

    pull_q = queue.Queue(EVENT_QUEUE_MAX)
    push_q = queue.Queue(EVENT_QUEUE_MAX)
    pending_event = threading.Event()
    camera_exists = False

    @staticmethod
    def get_api_url(api):
        """
        login to Server's API
        :return:
        """
        return "http://{0}:{1}/{2}/{3}/".format(
            str(CeeProxy.server_addr),
            str(CeeProxy.server_port),
            api,
            CeeProxy.device_id
        )

    @staticmethod
    def login():
        """
        login to Server's API
        :return:
        """
        logger.info('login')
        url = CeeProxy.get_api_url(SERVER_LOGIN_URL)

        while True:
            try:
                login = requests.get(url)
                if login.status_code == httplib.OK:
                    logger.info("login success")
                    return

            except Exception as e:
                logger.info(e.message)

            sleep(5)

    @staticmethod
    def server_pull():

        pull_url = CeeProxy.get_api_url(SERVER_PULL_URL)

        pull = requests.get(pull_url)

        try:

            if pull.status_code != httplib.OK:
                logger.info("status code: %d", pull.status_code)
                return None

            pull_data = pull.json()

            return pull_data

        except Exception as e:
            logger.info(e.message)
            return None

    @staticmethod
    def put_to_queue(q, data):
        """

        :param q:
        :param data:
        :return:
        """
        try:
            # fix 0.2: check queue is full, then pop older
            try:
                if q.full():
                    q.get_nowait()
            except queue.Empty:
                pass
            q.put_nowait(data)
        except queue.Full:
            pass

    @staticmethod
    def get_from_queue(q, timeout):
        """

        :param q:
        :param timeout:
        :return:
        """
        try:
            data = q.get(timeout=timeout)
        except queue.Empty:
            data = None
        return data

    @staticmethod
    def client_thread():

        logger.info('starting client thread')

        client_url = "http://" + CeeProxy.client_addr + ":" + str(CeeProxy.client_port)

        while True:
            api_req = CeeProxy.get_from_queue(CeeProxy.pull_q, 5)

            if api_req is None:
                continue

            api_url = client_url + api_req['api']
            logger.info(api_url)
            push = {
                "token": api_req['token'],
                "timestamp": '',
                "device_id": CeeProxy.device_id,
                "length": 0,
                "status": httplib.ACCEPTED,
                "data_format": '',
                "data": '',
            }

            try:
                # if data field in request then post() else get()
                if 'data' in api_req:
                    logger.info("post data: {}".format(api_req['data']))
                    if api_req['data'] == '':
                        api_res = requests.get(api_url)
                    else:
                        headers = {'Content-Type': 'application/json'}
                        api_res = requests.post(api_url, json=api_req['data'], headers=headers)
                else:
                    api_res = requests.get(api_url)

                # now parsing client's response
                content_len = int(api_res.headers['Content-Length'])
                push["timestamp"] = time.time()
                push["length"] = content_len
                push["status"] = api_res.status_code

                logger.info("push: {}".format(push))

                if api_res.status_code == httplib.OK:
                    try:
                        if content_len < 100000:
                            push["data_format"] = 'json'
                            push["data"] = api_res.json()
                        else:
                            push["data_format"] = 'raw'
                            push["data"] = api_res.content
                    except ValueError as e:
                        logger.error('Value error {}'.format(e))
                        logger.error('Value error {}'.format(api_res.raw.read(100)))
                        push["status"] = httplib.INTERNAL_SERVER_ERROR

            except Exception as e:
                logger.error('exception {}'.format(e.message))
                push["status"] = httplib.INTERNAL_SERVER_ERROR

            logger.info('put_to_queue')

            # put the push object to push_q then server_push_thread will push this to server
            CeeProxy.put_to_queue(CeeProxy.push_q, push)

            # set pending event to True so pull thread can get new pull request
            logger.info('set pending event')
            CeeProxy.pending_event.set()

    @staticmethod
    def server_push_thread():

        push_url = CeeProxy.get_api_url(SERVER_PUSH_URL)

        while True:
            push = CeeProxy.get_from_queue(CeeProxy.push_q, 5)

            if push is None:
                continue

            push_data = json.dumps(push)
            try:
                r = requests.post(url=push_url, json=push_data)

                if r.status_code != httplib.OK:
                    logger.error("push status code: %d", r.status_code)
                else:
                    push_res = r.json()
                    logger.info("push result: %s", push_res['code'])

            except Exception as e:
                logger.info(e.message)

            finally:
                pass

    @staticmethod
    def run():

        # set pending event to True
        logger.info('set pending event')
        CeeProxy.pending_event.set()

        # start client thread
        thread.start_new_thread(CeeProxy.client_thread, ())
        thread.start_new_thread(CeeProxy.server_push_thread, ())

        logger.info('start')

        while True:
            try:
                pull = CeeProxy.server_pull()

                if pull is None:
                    time.sleep(1)
                elif pull['code'] == 10:
                    time.sleep(1)
                else:
                    logger.info(pull)
                    # check pending event and if event is busy for 5 seconds then return
                    # device busy response
                    logger.info('check device status if can ready in 5 seconds')
                    error_resp = False
                    if not CeeProxy.pending_event.wait(timeout=0):

                        logger.info('device is still busy, response with LOCKED status')
                        CeeProxy.error_response(pull, httplib.LOCKED, 'device is busy')
                        error_resp = True

                    elif '/sapi/imgcap/' in pull['api']:
                        logger.info('image capture URL, check camera')
                        CeeProxy.camera_exists = camera_query()
                        if not CeeProxy.camera_exists:
                            logger.info('camera not found, response with 1002 status')
                            CeeProxy.error_response(pull, 1002, 'Camera capture failed: No Camera')
                            error_resp = True

                    if not error_resp:
                        logger.info('clear pending event')
                        CeeProxy.pending_event.clear()
                        CeeProxy.put_to_queue(CeeProxy.pull_q, pull)

            except Exception as e:
                logger.info(e.message)
                time.sleep(1)
            finally:
                time.sleep(1)
                pass

    @staticmethod
    def error_response(pull, status, data):
        push = {
            "token": pull['token'],
            "timestamp": time.time(),
            "device_id": CeeProxy.device_id,
            "length": len(data),
            "status": status,
            "data_format": 'raw',
            "data": data,
        }

        logger.info('put_to_queue')
        CeeProxy.put_to_queue(CeeProxy.push_q, push)


def daemon_proc():

    # options = get_options()
    # set_loggers(options.level, options.quiet)
    set_loggers()

    logger.info('CeeProxy')

    # find NIKON camera in usb devices and change mode to WRITE
    CeeProxy.camera_exists = camera_query()

    # load configuration from file
    SERVER_ADDR, SERVER_API_KEY, DEVICE_ID = load_config()

    CeeProxy.server_addr = SERVER_ADDR
    CeeProxy.server_port = SERVER_PORT
    CeeProxy.client_addr = CLIENT_ADDR
    CeeProxy.client_port = CLIENT_PORT
    CeeProxy.device_id = DEVICE_ID

    logger.info('after: %s' % SERVER_ADDR)

    # first login to server and receive access token
    CeeProxy.login()

    # go forever
    CeeProxy.run()


def main():
    # install_signal_handlers()
    with daemon.DaemonContext():
        daemon_proc()


if __name__ == "__main__":
    main()
