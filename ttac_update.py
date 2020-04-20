import configparser
import os
import sys

import loguru

from client_config import ClientConfig

from pyupdater.client import Client

from ttac_ver import Version

case = ''
cur_major = ''
cur_minor = ''
cur_patch = ''
curr_channel = ''


def app_info():
    version_string = Version.APP_VERSION
    channel = None
    major, minor, patch, channel, release = version_string.split('.')
    case = int(channel)
    if case == 0:
        channel = "alpha"
    elif case == 1:
        channel = "beta"
    elif case == 2:
        channel = "stable"
    else:
        channel = ""

    name = ClientConfig.APP_NAME
    version = f"{major}.{minor}.{patch}{channel}"
    return name, version


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


    APP_NAME, APP_VERSION = app_info()

    config = configparser.ConfigParser()
    config.read('config.ini')

    preferred_channel = config['pyupdater']['channel']
    stay_on_channel = config['pyupdater']['strict']

    strict = bool(stay_on_channel)

    if preferred_channel != ("alpha" or "beta" or "stable"):
        preferred_channel = ""
    app_update = client.update_check(APP_NAME, APP_VERSION, channel=preferred_channel, strict=strict)
    if app_update is not None:
        loguru.logger.info(f"[U] PYUPDATER DLI: ThunderTac v{APP_VERSION} is not the latest version")
        app_update.download()
        # if app_update.is_downloaded():
        #     with open('.ttacver', 'w') as f:
        #         f.write()
        if app_update.is_downloaded():
            app_update.extract_overwrite()
        if app_update.is_downloaded():
            app_update.extract_restart()
    else:
        loguru.logger.info(f"[U] PYUPDATER DLI: ThunderTac v{APP_VERSION} is the latest version")
