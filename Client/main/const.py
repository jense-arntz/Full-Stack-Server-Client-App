DEFAULT_SETTING_Field = ['5004',  # Compression Setting
                         '5005',  # White Balance
                         '5007',  # F-Number
                         '500b',  # Exposure Metering Mode
                         '500c',  # Flash Mode
                         '500f',  # Exposure Index
                         '5010',  # Exposure Bias Compensation
                         '5013',  # Still Capture Mode
                         'd054',  # Auto ISO
                         'd06b',  # Long Exposure Noise Reduction
                         'd161',  # Auto focus Mode
                         'd163',  # AF Assist Lamp
                         'd183'   # ISO Auto High Limit
                         ]
DEFAULT_SETTING_Value = ['2',  # Compression Setting
                         '4',  # White Balance
                         '1100',  # F-Number
                         '3',  # Exposure Metering Mode
                         '32784',  # Flash Mode
                         '800',  # Exposure Index
                         '0',  # Exposure Bias Compensation
                         '0',  # Still Capture Mode
                         '1',  # Auto ISO
                         '1',  # Long Exposure Noise Reduction
                         '4',  # Auto focus Mode
                         '1',  # AF Assist Lamp
                         '4'   # ISO Auto High Limit
                         ]

CAMERA_SETTING = {
    "jpeg-compression-settings": {
        "value": '5004',
        "JPEG Basic": '0',
        "JPEG Normal": '1',
        "JPEG Fine": '2'
    },
    "white-balance": {
        "value": '5005',
        "Automatic": '2',
        "Daylight": '4',
        "Incandescent": '5',
        "Flash": '6',
        "Cloudy": '7',
        "Shade": '32784'
    },
    "f-number": {
        "value": "5007",
        "3.5": '350',
        "3.8": '380',
        "4.0": '400',
        "4.5": '450',
        "5.0": '500',
        "5.6": '560',
        "6.3": '630',
        "7.1": '710',
        "8.0": '800',
        "9.0": '900',
        "10.0": '1000',
        "11.0": '1100',
        "13.0": '1300',
        "14.0": '1400',
        "16.0": '1600',
        "18.0": '1800',
        "20.0": '2000',
        "22.0": '2200'
    },
    "exposure-metering-mode": {
        "value": "500b",
        "Center Weighted Average": '2',
        "Multi-spot": '3',
        "Center-spot": '4',
    },
    "iso": {
        "value": "500f",
        "100": '100',
        "125": '125',
        "160": '160',
        "200": '200',
        "250": '250',
        "320": '320',
        "400": '400',
        "500": '500',
        "640": '640',
        "800": '800',
        "1000": '1000',
        "1250": '1250',
        "1600": '1600',
        "2000": '2000',
        "2500": '2500',
        "3200": '3200',
        "4000": '4000',
        "5000": '5000',
        "6400": '6400',
        "8000": '8000',
        "10000": '10000',
        "12800": '12800',
        "25600": '25600'
    },
    "exposure-compensation": {
        "value": "5010",
        "-5.000": '-5000',
        "-4.666": '-4666',
        "-4.333": '-4333',
        "-4.000": '-4000',
        "-3.666": '-3666',
        "-3.333": '-3333',
        "-3.000": '-3000',
        "-2.666": '-2666',
        "-2.333": '-2333',
        "-2.000": '-2000',
        "-1.666": '-1666',
        "-1.333": '-1333',
        "-1.000": '-1000',
        "-0.666": '-666',
        "-0.333": '-333',
        "0.0": '0',
        "+0.333": '333',
        "+0.666": '666',
        "+1.000": '1000',
        "+1.333": '1333',
        "+1.666": '1666',
        "+2.000": '2000',
        "+2.333": '2333',
        "+2.666": '2666',
        "+3.000": '3000',
        "+3.333": '3333',
        "+3.666": '3666',
        "+4.000": '4000',
        "+4.333": '4333',
        "+4.666": '4666',
        "+5.000": '5000'
    },
    "auto-iso": {
        "value": "d054",
        "On": '1',
        "Off":'0'
    },
    "long-exposure-noise-reduction": {
        "value": "d06c",
        "On": '1',
        "Off": '0'
    },
    "autofocus-mode": {
        "value": "d161",
        "AF-S": '0',
        "AF-C": '1',
        "AF-A": '2',
        "Manual": '3'
    },
    "af-assist-lamp": {
        "value": "d163",
        "On": '0',
        "Off": '1'
    },
    "auto-iso-hight-limit": {
        "value": "d183",
        "Hi 2": '5',
        "Hi 1": '4'
    }
}
