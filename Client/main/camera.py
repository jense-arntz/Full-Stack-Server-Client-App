from __future__ import print_function
import gphoto2 as gp
import json
import os
import re
import exifread
from main.const import *
from main.models import *
import subprocess
from main.logger import *


class MyCamera(object):
    """
    Init camera connection
    """
    def __init__(self):
        """
        Initialise the camera
        :return:
        """
        try:
            self.camera = gp.check_result(gp.gp_camera_new())
            self.context = gp.gp_context_new()
            self.path_root = '/camera/imgCap/'
            self.path_single = '/camera/imgCap/single/'
            self.path_hdr3 = '/camera/imgCap/hdr3/'
            self.path_hdr5 = '/camera/imgCap/hdr5/'

        except Exception as e:
            logger.error(e.message)

    def open(self):
        """
        open camera connection
        :return:
        """
        gp.check_result(gp.gp_camera_init(self.camera, self.context))

    def close(self):
        """
        Close camera connection
        :return:
        """
        # clean up
        gp.check_result(gp.gp_camera_exit(self.camera, self.context))

    def get_summary(self):
        """
        Get gphoto2 summary
        :return: json_data
        """
        text = gp.check_result(gp.gp_camera_get_summary(self.camera, self.context))
        content = str(text)

        search_text = {
            'manufacturer': 'Manufacturer: (.+)?',
            'model': 'Model: (.+)?',
            'version': 'Version: (.+)?',
            'serial_number': 'Serial Number: (.+)?',
            'free_space_sd_card': 'Free Space.+:(.+)?',
            'current_focal_length': 'Focal Length.+? value:(.+)?\(',
            'focus_mode': 'Focus Metering Mode.+? value:(.+)?\(',
            'exposure_time': 'Exposure Time.+? value:(.+)?\(',
            'exposure_program_mode': 'Exposure Program Mode.+? value:(.+)?\(',
            'jpeg_compression_settings': 'Compression Setting.+? value:(.+)?\(',
            'white_balance': 'White Balance.+? value:(.+)?\(',
            'f_number': 'F-Number.+? value: f/(.+)?\(',
            'exposure_metering_mode': 'Exposure Metering Mode.+? value:(.+)?\(',
            'flash_mode': 'Flash Mode.+? value:(.+)?\(',
            'exposure_compensation': 'Exposure Bias Compensation.+? value: ([-+]?\d+\.\d+)?.+?\(',
            'still_capture_mode': 'Still Capture Mode.+? value:(.+)?\(',
            'auto_iso': 'Auto ISO.+? value:(.+)?\(',
            'iso': 'Exposure Index.+? value: ISO(.+)?\(',
            'long_exposure_noise_reduction': 'Long Exposure Noise Reduction.+? value:(.+)?\(',
            'autofocus_mode': 'Autofocus Mode.+? value:(.+)?\(',
            'af_assist_lamp': 'AF Assist Lamp.+? value:(.+)?\(',
            'iso_auto_high_limit': 'ISO Auto High Limit.+? value:(.+)?\('
        }

        search_result = {}
        for tag in search_text:
            search_result[tag] = ''
            try:
                search_result[tag] = re.search(search_text[tag], content).group(1).strip()
            except Exception as e:
                logger.debug('exception: {}'.format(e))
                pass

        return [search_result]

    def get_config_value(self, field_name):
        """
        Get configValue for given configField
        :param field_name:
        :return:
        """
        # get configuration tree
        config = gp.check_result(gp.gp_camera_get_config(self.camera, self.context))
        # find the capture target config item
        config_target = gp.check_result(gp.gp_widget_get_child_by_name(config, str(field_name)))
        # check value in range
        value = gp.check_result(gp.gp_widget_get_value(config_target))
        return value

    def capture_image(self, method):
        """
        Capture image
        :param method:
        :return:
        """

        try:
            file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE, self.context))
            if method == 'single':
                path = self.path_single

            elif method == 'hdr3':
                path = self.path_hdr3

            elif method == 'hdr5':
                path = self.path_hdr5

            target = os.path.join(path, file_path.name)
            camera_file = gp.check_result(gp.gp_camera_file_get(self.camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL, self.context))
            gp.check_result(gp.gp_file_save(camera_file, target))
            # Count shutter count from image
            count = self.get_image_shutter(path + file_path.name)
            update_camera(str(count))

        except Exception as e:
            logger.error(e.message)

    def set_config_value(self, field_name, field_value):
        """
        Set configValue for given configField
        :param field_name:
        :param field_value:
        :return:
        """
        try:
            # get configuration tree
            config = gp.check_result(gp.gp_camera_get_config(self.camera, self.context))
            # find the capture target config item
            config_target = gp.check_result(gp.gp_widget_get_child_by_name(config, str(field_name)))
            # value = gp.check_result(gp.gp_widget_get_choice(config_target, 2))
            gp.check_result(gp.gp_widget_set_value(config_target, str(field_value)))
            # set config
            gp.check_result(gp.gp_camera_set_config(self.camera, config, self.context))
            logger.debug("set field_name:{}, field_value:{}".format(field_name, field_value))
        except Exception as e:
            logger.debug(e.message)

    def capture_single(self):
        """
        Capture Single Image
        :return: self.path_single
        """
        method = "single"
        subprocess.call(['tshwctl', '--redledoff'])
        try:
            self.capture_image(method)
            logger.debug("Capture Single Image OK!")
            subprocess.call(['tshwctl', '--redledon'])
            return self.path_single
        except Exception as e:
            logger.error(e.message)
            subprocess.call(['tshwctl', '--redledon'])
            return "error"

    def capture_hdr3(self):
        """
        Capture hdr3 Image
        :return: self.path_hdr3
        """
        method = 'hdr3'
        subprocess.call(['tshwctl', '--redledoff'])
        try:
            self.set_config_value('5010', '-3000')
            self.capture_image(method)
            self.set_config_value('5010', '+3000')
            self.capture_image(method)
            self.set_config_value('5010', '0')
            self.capture_image(method)
            # Compress the hdr3 images as hdr3.tar.gz
            MyCamera.compress_tar(source=self.path_hdr3, target=self.path_root + 'hdr3.tar.gz')
            path = self.path_hdr3 + "*"
            subprocess.call('rm -rf ' + path, shell=True)
            subprocess.call(['tshwctl', '--redledon'])
            return self.path_root
        except Exception as e:
            logger.error(e.message)
            subprocess.call(['tshwctl', '--redledon'])
            return "error"

    def capture_hdr5(self):
        """
        Capture hdr5 Image
        :return: self.path_hdr5
        """
        method = 'hdr5'
        subprocess.call(['tshwctl', '--redledoff'])
        try:
            self.set_config_value('5010', '-5000')
            self.capture_image(method)
            self.set_config_value('5010', '+5000')
            self.capture_image(method)
            self.set_config_value('5010', '-3000')
            self.capture_image(method)
            self.set_config_value('5010', '+3000')
            self.capture_image(method)
            self.set_config_value('5010', '0')
            self.capture_image(method)
            subprocess.call(['tshwctl', '--redledon'])
            # Compress the hdr3 images as hdr3.tar.gz
            MyCamera.compress_tar(source=self.path_hdr5, target=self.path_root + 'hdr5.tar.gz')
            path = self.path_hdr5 + "*"
            subprocess.call('rm -rf ' + path, shell=True)
            return self.path_root
        except Exception as e:
            logger.debug(e.message)
            subprocess.call(['tshwctl', '--redledon'])
            return "error"

    def reset_setting(self):
        """
        RESET CAMERA DEFAULT SETTING.
        :return:
        """
        for i in range(len(DEFAULT_SETTING_Field)):
            self.set_config_value(DEFAULT_SETTING_Field[i], DEFAULT_SETTING_Value[i])
            logger.debug("Reset Camera Setting OK!")
        return "success"

    def get_image_shutter(self, file_path):
        """
        Get shutter count from Image.
        :param file_path:
        :return:
        """
        count = " "
        try:
            f = open(file_path, 'rb')
            tags = exifread.process_file(f)
            f.close()
            count = tags['MakerNote TotalShutterReleases']
            return count
        except Exception as e:
            logger.error(e.message)
            return count

    def set_camera_setting(self, data):
        try:
            logger.debug("Start set camera setting")
            self.set_config_value(CAMERA_SETTING["af-assist-lamp"]["value"], CAMERA_SETTING["af-assist-lamp"][data["af-assist-lamp"]])
            self.set_config_value(CAMERA_SETTING["white-balance"]["value"], CAMERA_SETTING["white-balance"][data["white-balance"]])
            self.set_config_value(CAMERA_SETTING["jpeg-compression-settings"]["value"], CAMERA_SETTING["jpeg-compression-settings"][data["jpeg-compression-settings"]])
#            self.set_config_value(CAMERA_SETTING["f-number"]["value"], CAMERA_SETTING["f-number"][data["f-number"]])
            self.set_config_value(CAMERA_SETTING["exposure-metering-mode"]["value"], CAMERA_SETTING["exposure-metering-mode"][data["exposure-metering-mode"]])
            self.set_config_value(CAMERA_SETTING["iso"]["value"], CAMERA_SETTING["iso"][data["iso"]])
            self.set_config_value(CAMERA_SETTING["exposure-compensation"]["value"], CAMERA_SETTING["exposure-compensation"][data["exposure-compensation"]])
            self.set_config_value(CAMERA_SETTING["auto-iso"]["value"], CAMERA_SETTING["auto-iso"][data["auto-iso"]])
            self.set_config_value(CAMERA_SETTING["long-exposure-noise-reduction"]["value"], CAMERA_SETTING["long-exposure-noise-reduction"][data["long-exposure-noise-reduction"]])
            self.set_config_value(CAMERA_SETTING["autofocus-mode"]["value"], CAMERA_SETTING["autofocus-mode"][data["autofocus-mode"]])
            self.set_config_value(CAMERA_SETTING["auto-iso-hight-limit"]["value"], CAMERA_SETTING["auto-iso-hight-limit"][data["auto-iso-hight-limit"]])
            logger.debug("end camera setting")
        except Exception as e:
            logger.debug(e.message)

    @staticmethod
    def compress_tar(source, target):
        """
        Compress Function
        :param source:
        :param target:
        :return:
        """
        cmdline = ['/bin/tar', '-czvf', target, source]
        subprocess.call(cmdline)