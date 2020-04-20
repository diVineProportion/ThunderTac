import os
import re
import subprocess
import sys
import time

from ttac_new import app_info

if __name__ == "__main__":

    APP_VERSION = app_info()[1]

    os.system(f'pyupdater build --app-version={APP_VERSION} --pyinstaller-log-info win.spec')
    os.system('pyupdater pkg --process --sign')
    os.system('pyupdater upload --service scp')
