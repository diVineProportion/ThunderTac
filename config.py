import configparser
import json
import os
import subprocess
import sys

import requests


def ensure_config(_config_path):
    if not os.path.isfile(_config_path):
        ttac_cfg_file = 'https://raw.githubusercontent.com/diVineProportion/ThunderTac/master/config.ini'
        ttac_cfg_data = requests.get(ttac_cfg_file)
        with open(config_path, 'wb') as f:
            f.write(ttac_cfg_data.content)
        subprocess.call(["notepad.exe", config_path])


def ensure_not_first_run():
    config['configinit']['first_run'] = 'False'
    with open(config_path, 'w') as f:
        config.write(f)
    subprocess.call(["notepad.exe", config_path])


def cfg_loguru():
    ttac_log = config['loguru']['level']
    return ttac_log


def cfg_debug():
    ttac_dbg = config['debug']['debug_on']
    ttac_dbg = json.loads(ttac_dbg.lower())
    return ttac_dbg


def cfc_general():
    ttac_usr = config['general']['ttac_usr']
    ttac_mas = config['general']['ttac_mas']
    ttac_rec = config['general']['ttac_rec']
    return ttac_usr, ttac_mas, ttac_rec


def cfg_ftpcred():
    ftp_send = config['ftpcred']['ftp_send']
    ftp_addr = config['ftpcred']['ftp_addr']
    ftp_user = config['ftpcred']['ftp_user']
    ftp_pass = config['ftpcred']['ftp_pass']
    ftp_sess = config['ftpcred']['ftp_sess']
    ftp_send = json.loads(ftp_send.lower())
    return ftp_send, ftp_addr, ftp_user, ftp_pass, ftp_sess


def cfg_network():
    source_ip = config['network']['source_ip']
    source_pt = config['network']['source_pt']
    return source_ip, source_pt


def cfg_pyupdater():
    pyu_channel = config['pyupdater']['channel']
    pyu_strict = config['pyupdater']['strict']
    pyu_strict = json.loads(pyu_strict.lower())
    return pyu_channel, pyu_strict


def cfg_configinit():
    first_run = config['configinit']['first_run']
    first_run = json.loads(first_run.lower())
    if first_run:
        first_run = config['configinit']['first_run'] = 'False'
        first_run = json.loads(first_run.lower())
        with open(config_path, 'w') as f:
            config.write(f)
    return first_run


class WebInterfaceEndpoints:
    source_ip, source_pt = cfg_network()
    BASE = f"http://{source_ip}:{source_pt}"
    LMAP = f"{BASE}/map.img"
    INFO = f"{BASE}/map_info.json"
    STAT = f"{BASE}/state"
    INDI = f"{BASE}/indicators"
    OBJT = f"{BASE}/map_obj.json"
    CHAT = f"{BASE}/gamechat"
    HMSG = f"{BASE}/hudmsg"


if __name__ == "config":

    if getattr(sys, 'frozen', False):
        config_path = os.environ['LOCALAPPDATA'] + "\\warthunderapps\\thundertac\\update\\config.ini"
        ensure_config(config_path)
        config = configparser.ConfigParser()
        config.read(config_path)

    elif __file__:
        config_path = "config.ini"
        ensure_config(config_path)
        config = configparser.ConfigParser()
        config.read(config_path)

elif __name__ == "__main__":
    config_path = "config.ini"
    ensure_config(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
