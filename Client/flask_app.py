from flask import Flask, render_template, redirect,flash
from functools import wraps
from main.camera import *
from flask import request, url_for, session
from main.views import *
from main.logger import *
import json
import sqlite3
import logging
import base64

app = Flask(__name__, static_url_path='/static')
app.secret_key = "super secret key"
logger.addHandler(get_memory_log_handler())


def login_required(f):
    """
    Decorator for logged_in
    :param f:
    :return: f(*args, **kwargs)
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
    return wrap


def get_json_file_data(file_path, file_name):
    """
    Making json file for sending data to Server APP.
    :param file_path:
    :param file_name:
    :return:
    """
    file_one_path = file_path + file_name
    statinfo = os.stat(file_one_path)
    date_string = time.strftime("%Y-%m-%d-%H.%M")
    if 'jpg' in file_name:
        file_name = 'img-' + date_string + '.jpg'
    elif 'hdr3' in file_name:
        file_name = 'hdr3-' + date_string + '.tar.gz'
    elif 'hdr5' in file_name:
        file_name = 'hdr5-' + date_string + '.tar.gz'
    try:
        with open(file_one_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        json_data = json.dumps({'filename': file_name, 'size': statinfo.st_size, 'content': encoded_string})
        logger.debug('json file')
        return json_data
    except Exception as e:
        return json.dumps({})


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in page
    :return: render_template('Login.html', error=error)
    """
    error = None
    logger.debug(detect_empty_db())
    if detect_empty_db():
        insert_user_id()
    user_data = get_user_id()
    username = user_data[0]
    password = user_data[1]

    if request.method == 'POST':
        if request.form['username'].strip() != username or request.form['password'] != password:
            error = 'Invalid Credentials. Please try again.'
            logger.error("Invalid Credentials")
        else:
            session['logged_in'] = username
            logger.debug("%s Login OK!" % username)
            return redirect(url_for('main'))

    return render_template('Login.html', error=error)


@app.route('/logout')
def logout():
    """
    log out page
    :return: redirect(url_for('login'))
    """
    username = session['logged_in']
    session.clear()
    flash("You have been logged out!")
    logger.debug("%s Logout OK!" % username)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def main():
    """
    Display Main Page.
    :return: render_template('Main.html', name=name)
    """
    name = session['logged_in']
    return render_template('Network_settings.html', name=name)


@app.route('/Network_Settings')
@login_required
def network_setting():
    """
    Display Network Settings Page.
    :return: render_template('Network_settings.html', name=name)
    """
    logger.info("GET DNS[1] OK!")
    name = session['logged_in']
    return render_template('Network_settings.html', name=name)


@app.route('/Remote_Communication')
@login_required
def remote_communication():
    """
    Display Remote Communications Page.
    :return: render_template('Remote_communication.html', name=name)
    """
    name = session['logged_in']
    return render_template('Remote_communication.html', name=name)


@app.route('/Camera_Config')
@login_required
def camera_config():
    """
    Display Camera Config Page.
    :return: render_template('Camera_Config.html', name=name)
    """
    name = session['logged_in']
    return render_template('Camera_Config.html', name=name)


@app.route('/System_Settings')
@login_required
def system_config():
    """
    Display System Settings.
    :return: render_template('System_settings.html', name=name)
    """
    name = session['logged_in']
    return render_template('System_settings.html', name=name)


@app.route('/Log/<option>')
@login_required
def log_option(option):
    """
    Display Log Page depending on 'App' or 'Sys'.
    :param option:
    :return:
    """
    name = session['logged_in']
    if option == 'App':
        return render_template('Log_App.html', name=name)

    elif option == 'Sys':
        return render_template('Log_Sys.html', name=name)


@app.route('/api/log/<option>')
@login_required
def read_logs(option):
    """
    Get the Log datas from log file.
    :param option:
    :return:
    """
    if option == 'App' or option == 'Sys':
        log_content = get_log_data(option)
        logger.debug("READ %s LOG OK!" % option)
        return log_content

    elif option == 'Clearapp':
        msg = clear_log_data()
        logger.debug("Clear APP Log %s" % msg)
        return msg

    elif option == 'Clearsys':
        msg = clear_log_sys()
        logger.debug("Clear SYS Log %s" % msg)
        return msg

    else:
        logger.error("No FOUND API")


@app.route('/api/get/log')
def get_device_logs():
    """
    Get Log and send Log to server
    :return:
    """
    logger.debug("READ AppLog")
    code =0
    try:
        log_content = get_log_data('App')
        logger.debug("READ App LOG OK!")
        logger.debug(log_content)
        return log_content

    except Exception as e:
        logger.debug(e.message)
        code = 1
        ret = {
            'status': code,
        }
        return json.dumps(ret)


@app.route('/api/sys/summary')
def get_system_summary():
    """
    Get the System Summary
    :return: json_data
    """
    logger.debug("ok")
    host = Get_Setting()
    # --------- Get DNS server IP. ------------
    nameservers = host.get_dns()

    if len(nameservers) == 1:
        dns_1 = nameservers[0]
        dns_2 = "None Set"
        logger.debug("GET DNS[1] OK!")
    elif len(nameservers) >= 2:
        dns_1 = nameservers[0]
        dns_2 = nameservers[1]
        logger.debug("GET DNS[1],[2] OK!")
    else:
        logger.error("None DNS")
    # ----------Get IP mode------------------
    ip_mode = host.get_mode()
    if ip_mode is None:
        logger.debug("GET IP MODE OK!")
    else:
        logger.error("None IP MODE")
    # ----------Get Server address------------
    server_addr = host.get_server_addr()

    if server_addr:
        logger.debug("GET SERVER ADDRESS OK!")
    else:
        logger.error("None SERVER ADDRESS")

    # ---------- Get Timedate ----------------
    timedate = host.get_time()
    if timedate is None:
        logger.error("None Time")
    else:
        logger.debug('GET Time OK!')
    # ---------- Get token -------------------
    token = host.get_token()
    if token is None:
        logger.error("None TOKEN")
    else:
        logger.debug('GET TOKEN OK!')
    # ----------Get shuttercount -----------

    json_data = json.dumps({'device_ip': host.ipaddress, 'device_subnetmask': host.subnet, 'server_addr': server_addr, 'device_gateway': host.gateways,
                            'dns_1': dns_1, 'dns_2': dns_2, 'hostname': host.hostname, 'mac': host.mac,
                            'version': host.os_ver, 'os': host.os, 'token': token, 'device_ipmode': ip_mode, 'time': timedate})

    logger.debug("SEND IP JSON OK!")

    return json_data


# --------------------------------- Update the Ip settings to DB --------------------------------
@app.route('/api/sys/update', methods=["POST"])
@login_required
def update_system_summary():
    """
    Update the Ip settings to DB
    :return:
    """
    update = Update_Setting()
    hostname = request.form['hostname']
    ip_mode = request.form['ip_mode']
    subnet_mask = request.form['subnet_mask']
    gateway = request.form['gateway']
    if hostname is None:
        logger.error("HOSTNAME IS EMPTY")
        return "error"
    else:
        if ip_mode == "Static":
            dns_1 = request.form['dns1']
            dns_2 = request.form['dns2']
            ip_address = request.form['ip_address']
            mask = request.form['subnet_mask']
            gateway = request.form["gateway"]
            update.update_host(hostname)
            update.dns(dns_1, dns_2)
            update.static(ip_address, mask, gateway)
        else:
            update.update_host(hostname)
            update.dhcp()
        return "Success"


# TODO -------send token to Server when generate token-----------------
@app.route('/api/sys/update_token')
def update_device_token():
    """
    Update Setup-token to DB
    :return: token
    """
    update = Update_Setting()
    token = update.generate_token()

    if token is None:
        logger.error("No UPDATE TOKEN")
    else:
        logger.debug("UPDATE TOKEN OK!")

    return token


@app.route('/api/sys/update_server', methods=["POST"])
def update_device_server():
    """
    Update server_addr to DB
    :return: "success"
    """
    server_addr = request.form["server"]
    token = request.form["token"]

    if server_addr is None:
        logger.error("SERVER ADDRESS EMPTY")
        return "error"
    else:
        try:
            update_ip(token, server_addr)
            logger.debug("UPDATE SERVER ADDRESS OK!")
            host = Get_Setting()

            if not host.push_token(server_addr, token):
                logger.debug("PUSH TOKEN FAILED")
                return "push token failed"
        except sqlite3.Error as e:
            logger.error(e.message)
            return "error"
    return "success"


@app.route('/api/sys/update_setting', methods=["POST"])
def update_sys_setting():
    """
    Update new password to DB
    :return: "success" or "error"
    """
    update = Update_Setting()
    password_0 = request.form["password_0"]
    password_1 = request.form["password_1"]
    date_time = request.form["date_time"]
    # update.set_time(str(date_time))
    # logger.debug("CHANGE DATETIME OK!")

    if password_0 is None or password_1 is None:
        logger.error("NEW PASSWORD EMPTY")
        return "INVALID PASSWORD"
    else:
        username = session['logged_in']
        if password_0 == password_1:
            update_user_id(username, password_0)
            logger.debug("CHANGE PASSWORD OK!")
            return "success"

        else:
            logger.error("PASSWORD no MATCH")
            return "error"


# =========================== About CAMERA =================================
@app.route('/api/control/summary')
def get_camera_summary():
    """
    Get Camera Setting
    :return: json_data
    """
    data = ''
    try:
        camera = MyCamera()
        camera.open()
        json_data = camera.get_summary()
        camera.close()
        shutter_count = get_shuttercount()
        json_data[0]['shutter_count'] = shutter_count
        data = json.dumps(json_data)
        logger.debug("JSON DATA OK!")
    except Exception as e:
        logger.error(e.message)
    return data


@app.route('/api/control/<configField>')
def get_configfield_value(configField):
    """
    Get [configValue] for that [configField]
    :param configField:
    :return: 'configField = %s, configValue = %s' % (configField, config_value)
    """
    code = 0

    try:
        camera = MyCamera()
        camera.open()
        config_value = camera.get_config_value(configField)
        camera.close()
        logger.debug("GET VALUE of [%s] OK!" % configField)
    except Exception as e:
        logger.error(e.message)
        code = 1

    ret = {
        'status': code,
        'config-field': configField,
        'config-value': config_value
    }

    return json.dumps(ret)


@app.route('/api/control/<configField>/<configValue>')
def set_configfield_value(configField, configValue):
    """
    Get [configValue] for that [configField]
    :param configField:
    :param configValue:
    :return: "Successful: Set configField = %s, configValue = %s" % (configField, configValue)
    """
    code = 0
    try:
        camera = MyCamera()
        camera.open()
        camera.set_config_value(configField, configValue)
        camera.close()
        logger.debug("SET VALUE [{}] of [{}] OK!".format(configValue, configField))

    except Exception as e:
        logger.debug('set_configfield_value {}'.format(e.message))
        code = 1

    ret = {
        'status': code,
        'config-field': configField,
        'config-value': configValue
    }

    return json.dumps(ret)


@app.route('/api/control/config', methods=["POST"])
def set_control_config():
    """
    Set camera setting from Server.
    :return: code
    """
    try:
        data = request.get_json()
        camera = MyCamera()
        camera.set_camera_setting(data)
        code = 0
    except Exception as e:
        code = 1

    ret = {
        'status': code
    }

    return json.dumps(ret)


@app.route('/api/camera/reset')
def set_camera_default():
    """
    Reset Camera default setting.
    :return:
    """
    try:
        camera = MyCamera()
        camera.open()
        msg = camera.reset_setting()
        camera.close()
        logger.debug("RESET CAMERA SETTING OK!")
        return msg
    except Exception as e:
        logger.error(e.message)
        return "error"


@app.route('/api/imgcap/single')
def get_imgcap_single():
    """
    Get single image (Client)
    :return: filepath + 'capt0000.jpg'
    """
    try:
        camera = MyCamera()
        camera.open()
        filepath = camera.capture_single()
        camera.close()
        logger.debug("SINGLE IMAGE CAPTURE OK!")
        if filepath == 'error':
            return "error"
        else:
            return filepath + 'capt0000.jpg'

    except Exception as e:
        logger.error(e.message)
        return "Capture failed"


@app.route('/sapi/imgcap/single')
def sapi_imgcap_single():
    """
    Get single image (Server)
    :return: get_json_file_data(file_path=filepath, file_name='capt0000.jpg')
    """
    filepath = ""
    try:
        camera = MyCamera()
        camera.open()
        filepath = camera.capture_single()
        camera.close()
        logger.debug("SERVER: SINGLE IMAGE CAPTURE OK!")
        return get_json_file_data(file_path=filepath, file_name='capt0000.jpg')

    except Exception as e:
        logger.error(e.message)
        return json.dumps({'filename': '', 'size': 0, 'content': {}})


@app.route('/api/imgcap/hdr3')
def get_imgcap_hdr3():
    """
    Get hdr3 image (Client)
    :return: filepath + 'hdr3.tar.gz'
    """
    try:
        camera = MyCamera()
        camera.open()
        filepath = camera.capture_hdr3()
        camera.close()
        logger.debug("HDR3 CPATURE OK!")
        return filepath + 'hdr3.tar.gz'

    except Exception as e:
        logger.error(e.message)
        return "error"


@app.route('/sapi/imgcap/hdr3')
def sapi_imgcap_hdr3():
    """
    Get hdr3 image (Server)
    :return: get_json_file_data(file_path=filepath, file_name='hdr3.tar.gz')
    """
    try:
        camera = MyCamera()
        camera.open()
        filepath = camera.capture_hdr3()
        camera.close()
        logger.debug("SERVER:HDR3 CPATURE OK!")
        return get_json_file_data(file_path=filepath, file_name='hdr3.tar.gz')

    except Exception as e:
        logger.error(e.message)
        return json.dumps({'filename': '', 'size': 0, 'content': {}})


@app.route('/api/imgcap/hdr5')
def get_imgcap_hdr5():
    """
    Get hdr5 image (Client)
    :return: filepath + 'hdr5.tar.gz'
    """
    try:
        camera = MyCamera()
        camera.open()
        filepath = camera.capture_hdr5()
        camera.close()
        logger.debug("HDR5 CAPTURE OK!")
        return filepath + 'hdr5.tar.gz'

    except Exception as e:
        logger.error(e.message)
        return "Capture failed"


@app.route('/sapi/imgcap/hdr5')
def sapi_imgcap_hdr5():

    """
    Get hdr5 image(Server)
    :return: get_json_file_data(file_path=filepath, file_name='hdr5.tar.gz')
    """
    try:
        camera = MyCamera()
        camera.open()
        filepath = camera.capture_hdr5()
        camera.close()
        logger.debug("SERVER:HDR5 CAPTURE OK!")
        return get_json_file_data(file_path=filepath, file_name='hdr5.tar.gz')

    except Exception as e:
        logger.error(e.message)
        return json.dumps({'filename': '', 'size': 0, 'content': {}})


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0')
