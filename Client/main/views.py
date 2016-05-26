import os, platform, socket
import netifaces as ni
import uuid
import re
import subprocess
from subprocess import call
import json
from uuid import getnode as get_mac
from main.models import *
from main.logger import *
import requests
import httplib


def clear_log_data():
    """
    Clear APP Log Data
    :return: "success"
    """
    file_path = LOG_FILE
    try:
        with open(file_path, "w"):
            pass
    except Exception as e:
        logger.error(e.message)
    logger.debug("Clear APP Log OK!")

    return "success"


def clear_log_sys():
    """
    Clear SYS Log Data
    :return: "success"
    """
    file_path = LOG_SYSFILE
    try:
        fopen = open(file_path, "w")
        fopen.truncate()
        fopen.close()
    except Exception as e:
        logger.error(e.message)
    logger.debug("Clear SYS Log OK!")

    return "success"


def get_shuttercount():
    """
    Get shutter count
    :return: shuttercount
    """
    shuttercount = get_camera()[0]
    logger.debug("GET shuttercount %s OK!" % shuttercount)
    return shuttercount


def get_log_data(option):
    """
    Get log data from log file
    :param option:
    :return: log_data
    """
    if option == 'App':
        file_path = LOG_FILE

    elif option == 'Sys':
        file_path = LOG_SYSFILE

    try:
        fopen = open(file_path, 'r')

        line = fopen.read().strip()

        log_data = json.dumps({'log': line})

        fopen.close()

        logger.debug("READ %s LOG OK!" % option)

        return log_data

    except Exception as e:
        logger.error(e.message)
        return "error"


class Get_Setting():
    """
    Get system setting
    """

    def __init__(self):
        # ----------------- NIC INFO -----------------
        self.os = platform.dist()[0]
        # If system is "debian":
        if self.os == 'debian':
            self.hostname = socket.gethostname()
            self.iface = ni.interfaces()[1]
            self.ipaddress = ni.ifaddresses(self.iface)[ni.AF_INET][0]['addr']
            self.subnet = ni.ifaddresses(self.iface)[ni.AF_INET][0]['netmask']
            self.gateways = ni.gateways()['default'][ni.AF_INET][0]
            # --- OS INFO ---------------------

            self.os_ver = platform.dist()[1]
            self.mac = ''.join('%012x' % get_mac())
            self.ip_data = get_ip()
            self.path_ip = '/etc/network/interfaces'
            self.dns_file = '/etc/resolv.conf'
        # If system is "Arch Linux":
        else:
            self.hostname = socket.gethostname()
            self.iface = ni.interfaces()[1]
            self.ipaddress = ni.ifaddresses(self.iface)[ni.AF_INET][0]['addr']
            self.subnet = ni.ifaddresses(self.iface)[ni.AF_INET][0]['netmask']
            self.gateways = ni.gateways()['default'][ni.AF_INET][0]
            # --- OS INFO ---------------------
            self.os_ver = platform.dist()[1]
            self.mac = ''.join('%012x' % get_mac())
            self.ip_data = get_ip()
            self.path_ip = '/etc/netctl/eth0'
            self.dns_file = '/etc/resolv.conf'
        logger.debug('GET IP SETTING OK!')

    def get_time(self):
        """
        Get system time date
        :return: sys_time
        """
        if self.os == 'debian':
            sys_time = subprocess.check_output("date", shell=True)
        else:
            time_data = subprocess.check_output("timedatectl | grep Local", shell=True)
            sys_time = re.search('.(\w+).(\d+)-(\d+)-(\d+).(\d+):(\d+):(\d+)', time_data).group().strip()
        return sys_time

    def push_token(self, server_addr, token):
        # push token to server
        url = "http://{}/api/client/token/{}/{}/".format(server_addr, self.mac, token)
        api_res = requests.get(url)

        if api_res.status_code != httplib.OK:
            logger.debug("status code: %d", api_res.status_code)
            return False

        return True

    def get_token(self):
        """
        Get token
        :return: token
        """
        try:
            token = self.ip_data[0]
            logger.debug("GET TOKEN OK!")
            return token
        except Exception as e:
            logger.error(e.message)
            token = ''
            return token

    def get_server_addr(self):
        """
        Get Server address
        :return: server_addr
        """
        try:
            server_addr =self.ip_data[2]
            logger.debug("GET SERVER ADDRESS OK!")
            return server_addr
        except Exception as e:
            logger.error(e.message)
            server_addr = " "
            return server_addr

    def get_mode(self):
        """
        Get Device IP mode.
        :return:
        """
        if self.os == 'debian':
            with open(self.path_ip, 'r') as inF:
                    for line in inF:
                        if 'dhcp' in line:
                            mode = 'DHCP'
                            break
                        if 'static' in line:
                            mode = 'Static'
                            break
            inF.close()
            return mode
        else:
            if os.path.exists(self.path_ip):
                with open(self.path_ip, 'r') as inF:
                    for line in inF:
                        if 'dhcp' in line:
                            mode = 'DHCP'
                            break
                        if 'static' in line:
                            mode = 'Static'
                            break
                inF.close()
            else:
                mode = 'DHCP'
            return mode

    def get_dns(self):
        """
        Get DNS SERVER IP Address
        :return: nameservers
        """
        nameservers = []

        try:
            rconf = open(self.dns_file, "r")
            line = rconf.readline()
            while line:
                try:
                    ip = re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line).group()
                    nameservers.append(ip)

                except:
                    line = rconf.readline()
                    continue
                line = rconf.readline()
            rconf.close()
            return nameservers
        except Exception as e:
            logger.error(e.message)
            return nameservers


class Update_Setting():
    """
    Update settings
    """

    def __init__(self):
        self.os = platform.dist()[0]
        if self.os == 'debian':
            self.path_ip = '/etc/network/interfaces'
            self.dns_file = '/etc/resolv.conf'
        else:
            logger.debug("Arch")
            self.path_ip = '/etc/netctl/'
            self.dns_file = '/etc/resolv.conf'

    # ---------------------------Generate Token-------------------------------
    def generate_token(self):
        token = str(uuid.uuid4())
        if token is None:
            logger.error('None TOKEN GENERATE')
        else:
            logger.debug('TOKEN GENERATE OK!')
        return token

    # --------------------------- Change Ip to Static -------------------------
    def static(self, address, subnet, gateway):
        if self.os == 'debian':
            full_path = os.path.join(self.path_ip)
            fo = open(full_path, "w+")
            content = "auto lo\n" \
                      "iface lo inet loopback\n" \
                      "\n" \
                      "auto eth0\n" \
                      "iface eth0 inet static\n" \
                     "address " + address + "\n" + "gateway " + gateway + "\n" + "netmask" + subnet + "\n"
            fo.write(content)
            fo.close()
            os.system("sudo /etc/init.d/networking restart")

        else:
            full_path = os.path.join(self.path_ip, "eth0")
            fo = open(full_path, "w+")
            content = "Interface=eth0\nConnection=ethernet\nIP=static\nAddress=(\'" + \
                      address + "\')\nNetmask=(\'" + \
                      subnet + "\')\nGateway=(\'" + \
                      gateway + "\')\n"
            fo.write(content)
            fo.close()
            os.system("sudo netctl start eth0")
            os.system("sudo netctl enable eth0")

    def dhcp(self):
        """
        Change IP for dhcp
        :return:
        """
        if self.os == 'debian':
            full_path = os.path.join(self.path_ip)
            fo = open(full_path, "w+")
            content = "auto lo\n" \
                      "iface lo inet loopback\n" \
                      "\n" \
                      "auto eth0\n" \
                      "iface eth0 inet \n"
            fo.write(content)
            fo.close()
            os.system("sudo /etc/init.d/networking restart")

        else:
            full_path = os.path.join(self.path_ip, "eth0")
            fo = open(full_path, "w+")
            content = "Interface=eth0\nConnection=ethernet\nIP=dhcp\n"
            fo.write(content)
            fo.close()
            os.system("sudo netctl start eth0")
            os.system("sudo netctl enable eth0")


    def update_host(self, hostname=""):
        """
        Change hostname
        :param hostname:
        :return:
        """
        if self.os == 'debian':
            hosts_file = '/etc/hosts'
            hostname_file = '/etc/hostname'
            f_hostname = open(hostname_file, "r")
            old_hostname = f_hostname.readline()
            old_hostname = old_hostname.replace('\n', '')
            old_hostname = old_hostname.strip()
            f_hostname.close()
            f_hostname = open(hostname_file, "w")
            f_hostname.write(hostname)
            f_hostname.close()

            f_hosts = open(hosts_file, "r")
            set_host = f_hosts.read()
            f_hosts.close()
            set_host_file = open(hosts_file, "w")
            content = set_host.replace(old_hostname, hostname)
            set_host_file.write(content)
            set_host_file.close()
        else:
            os.system("hostnamectl set-hostname " + hostname)

    def dns(self, dns_1="", dns_2=""):
        """
        Change DNS name
        :param dns_1:
        :param dns_2:
        :return:
        """

        f_dns = open(self.dns_file, "w")
        if dns_1 != "":
            f_dns.writelines("nameserver" + " " + dns_1 + "\n")

        if dns_2 != "":
            f_dns.writelines("nameserver" + " " + dns_2 + "\n")
        f_dns.close()
