import os
import re
import subprocess
import sys
import time

from client_config import ClientConfig

client = ClientConfig


if __name__ == "__main__":

    APP_NAME = client.APP_NAME

    with open('.ttacver', 'r') as r:
        version_file = r.read()

    cur_major, cur_minor, cur_patch, cur_channel, release = version_file.split('.')
    cur_channel = int(cur_channel)
    if cur_channel == 0:
        APP_CHANNEL = "alpha"
    elif cur_channel == 1:
        APP_CHANNEL = "beta"
    elif cur_channel == 2:
        APP_CHANNEL = "stable"

    APP_VERSION = f"{cur_major}.{cur_minor}.{cur_patch}{APP_CHANNEL}"

    os.system(f'pyupdater build --app-version={APP_VERSION} --pyinstaller-log-info win.spec')
    os.system('pyupdater pkg --process --sign')
    os.system('pyupdater upload --service scp')
