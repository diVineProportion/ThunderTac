import configparser
import os
import loguru
import requests


if not os.path.isfile('config.ini'):
    loguru.logger.error(f"[I] ASSET MISSING: 'config.ini'")
    loguru.logger.info(f"[I] GETTING ASSET: 'config.ini'")
    ttac_cfg_file = 'https://raw.githubusercontent.com/diVineProportion/ThunderTac/master/config.ini'
    ttac_cfg_data = requests.get(ttac_cfg_file)
    with open('config.ini', 'wb') as f:
        f.write(ttac_cfg_data.content)

config = configparser.ConfigParser()
config.read('config.ini')
source_ip = config['network']['source_ip']
source_pt = config['network']['source_pt']


class WebAPI:
    BASE = f"http://{source_ip}:{source_pt}"
    LMAP = f"{BASE}/map.img"
    INFO = f"{BASE}/map_info.json"
    STAT = f"{BASE}/state"
    INDI = f"{BASE}/indicators"
    OBJT = f"{BASE}/map_obj.json"
    CHAT = f"{BASE}/gamechat"
    HMSG = f"{BASE}/hudmsg"
