import configparser
import json
import os
import subprocess
import sys

import requests


config_file = "config.ini"
config_root = f"{os.environ['LOCALAPPDATA']}\\WarThunderApps\\ThunderTac"
config_path = f"{config_root}\\{config_file}"


def ensure_config():
    if not os.path.exists(config_root):
        os.makedirs(config_root, exist_ok=True)
    if not os.path.isfile(config_path):
        ttac_cfg_file = 'https://raw.githubusercontent.com/diVineProportion/ThunderTac/rewrite/config.ini'
        ttac_cfg_data = requests.get(ttac_cfg_file)
        with open(config_path, 'wb') as f:
            f.write(ttac_cfg_data.content)


def cfg_loguru():
    config = configparser.ConfigParser()
    config.read(config_path)
    logger_l = config['loguru']['logger_l']
    return logger_l


def cfg_debug():
    config = configparser.ConfigParser()
    config.read(config_path)
    debug_on = config['debug']['debug_on']
    debug_on = json.loads(debug_on.lower())
    return debug_on


def cfc_general():
    config = configparser.ConfigParser()
    config.read(config_path)
    ttac_usr = config['general']['ttac_usr']
    ttac_mas = config['general']['ttac_mas']
    ttac_rec = config['general']['ttac_rec']
    return ttac_usr, ttac_mas, ttac_rec


def cfg_ftpcred():
    config = configparser.ConfigParser()
    config.read(config_path)
    ftp_send = config['ftpcred']['ftp_send']
    ftp_addr = config['ftpcred']['ftp_addr']
    ftp_user = config['ftpcred']['ftp_user']
    ftp_pass = config['ftpcred']['ftp_pass']
    ftp_sess = config['ftpcred']['ftp_sess']
    ftp_send = json.loads(ftp_send.lower())
    return ftp_send, ftp_addr, ftp_user, ftp_pass, ftp_sess


def cfg_network():
    ensure_config()
    config = configparser.ConfigParser()
    config.read(config_path)
    net_host = config['network']['net_host']
    net_port = config['network']['net_port']
    return net_host, net_port


def cfg_pyupdater():
    config = configparser.ConfigParser()
    config.read(config_path)
    pyu_uchn = config['pyupdater']['pyu_uchn']
    pyu_schn = config['pyupdater']['pyu_schn']
    pyu_schn = json.loads(pyu_schn.lower())
    return pyu_uchn, pyu_schn


def cfg_configinit():
    config = configparser.ConfigParser()
    config.read(config_path)
    init_run = config['configinit']['init_run']
    init_run = json.loads(init_run.lower())
    return init_run


def cfg_set_init():
    init_run = cfg_configinit()
    config = configparser.ConfigParser()
    config.read(config_path)
    if init_run:
        init_run = config['configinit']['init_run'] = 'False'
        init_run = json.loads(init_run.lower())
        with open(config_path, 'w') as f:
            config.write(f)


class WebInterfaceEndpoints:
    net_host, net_port = cfg_network()
    BASE = f"http://{net_host}:{net_port}"
    LMAP = f"{BASE}/map.img"
    INFO = f"{BASE}/map_info.json"
    STAT = f"{BASE}/state"
    INDI = f"{BASE}/indicators"
    OBJT = f"{BASE}/map_obj.json"
    CHAT = f"{BASE}/gamechat"
    HMSG = f"{BASE}/hudmsg"


# if __name__ == "config":
#
#     if getattr(sys, 'frozen', False):
#         ensure_config(config_path)
#         config = configparser.ConfigParser()
#         config.read(config_path)
#
#     elif __file__:
#         ensure_config(config_path)
#         config = configparser.ConfigParser()
#         config.read(config_path)
#
# elif __name__ == "__main__":
#     ensure_config(config_path)
#     config = configparser.ConfigParser()
#     config.read(config_path)
