import subprocess
import os
import re
import stat
from const import *


MODE_WRITE = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH


def chmod_usb_dev(file_path, mode):
    try:
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | mode )
        return True
    except:
        return False


def camera_query():
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb", shell=True)
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)

    for d in devices:
        if d['id'] == NIKON_CAMERA_ID:
            chmod_usb_dev(file_path=d['device'], mode=MODE_WRITE)
            return True

    return False
