import configparser
import os
import sys

import loguru
from pyupdater.client import Client

from client_config import ClientConfig


def progress_bar(percent):
    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(percent * 50), percent*100), end="", flush=True)


def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    percent_complete = info.get(u'percent_complete')
    time = info.get(u'time')
    progress_bar(percent_complete)
    # print(downloaded, total, status, percent_complete, time)


invoker = __name__
if invoker == "__main__":
    # TODO: Manual Update Check & Update
    input("Press any key to exit..")
    sys.exit()

elif invoker == "auto_update":
    client = Client(ClientConfig())
    client.refresh()
    client.add_progress_hook(print_status_info)

    # try:
    #     pyu_information_latest_alpha_win = client.json_data['latest']['ThunderTac']['alpha']['win']
    #     pyu_information_latest_beta_win = client.json_data['latest']['ThunderTac']['beta']['win']
    #     pyu_information_updates = client.json_data['updates']
    # except KeyError:
    #     pass

    APP_NAME = ClientConfig.APP_NAME

    with open('.ttacver', 'r') as r:
        version_file = r.read()

    if os.stat('.ttacver').st_size == 0:
        print('File is empty')
    else:
        cur_major, cur_minor, cur_patch, cur_channel, release = version_file.split('.')

        cur_channel = int(cur_channel)
        if cur_channel == 0:
            CUR_APP_CHANNEL = "alpha"
        elif cur_channel == 1:
            CUR_APP_CHANNEL = "beta"
        elif cur_channel == 2:
            CUR_APP_CHANNEL = "stable"

    if cur_channel != 2:
        APP_VERSION = f"{cur_major}.{cur_minor}.{cur_patch}{CUR_APP_CHANNEL}"
    else:
        APP_VERSION = f"{cur_major}.{cur_minor}.{cur_patch}"

    config = configparser.ConfigParser()
    config.read('config.ini')

    preferred_channel = config['pyupdater']['channel']
    stay_on_channel = config['pyupdater']['strict']

    strict = bool(stay_on_channel)

    if preferred_channel != ("alpha" or "beta" or "stable"):
        preferred_channel = ""
    app_update = client.update_check(APP_NAME, APP_VERSION, channel=preferred_channel, strict=strict)

    if app_update is not None:
        app_update.download()
        # if app_update.is_downloaded():
        #     with open('.ttacver', 'w') as f:
        #         f.write()
        if app_update.is_downloaded():
            app_update.extract_overwrite()
        if app_update.is_downloaded():
            app_update.extract_restart()
    else:
        loguru.logger.info(f"[U] PYUPDATER DLI: ThunderTac v{APP_VERSION} is the latest .ttacver.")
