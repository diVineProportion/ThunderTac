import argparse
import os
import re
import subprocess
import sys
import time


if __name__ == "__main__":

    # from client_config import ClientConfig
    # APP_VERSION = ClientConfig.APP_VERSION
    #
    # major, minor, patch, channel, release = APP_VERSION.split('.')

    # major = input("major: ")
    # minor = input("minor: ")
    # patch = input("patch: ")
    # channel = input("channel: ")
    # release = input("release: ")

    client_version = input(f'{{major}}.{{minor}}.{{patch}}.{{channel}}.{{release}}: ')


    client_write = f'''class ClientConfig(object):
    PUBLIC_KEY = 'gp4xou4FKWdJGoiMHaXH5EMSG7qafZtPqCnLJ0DRxZU'
    APP_NAME = 'ThunderTac'
    APP_VERSION = '{client_version}'
    COMPANY_NAME = 'WTApps'
    HTTP_TIMEOUT = 30
    MAX_DOWNLOAD_RETRIES = 3
    UPDATE_URLS = ['https://github.com/diVineProportion/pyutest/raw/main/',
                   'https://github.com/diVineProportion/pyutest/blob/main/',
                   'https://raw.githubusercontent.com/diVineProportion/pyutest/main/']'''

    with open('pyu_config.py', 'w') as f:
        f.write(client_write)
    with open('../../__init__.py', 'w') as f:
        f.write(f'__version__ = "{client_version}"')

    # if channel == ("0" or ""):
    #     channel = ""
    # if channel == ("1" or "a" or "alpha"):
    #     channel = "alpha"
    # if channel == ("2" or "b" or "beta"):
    #     channel = "beta"

    cli_version = input(f'{{major}}.{{minor}}.{{patch}}.{{channel}}.{{release}}: ')

    os.system(f'pyupdater build --app-version={cli_version} --pyinstaller-log-info win.spec')
    os.system('pyupdater pkg --process')
    os.system('pyupdater pkg --sign')
    os.system('cd pyu-data\\deploy')
    os.system('git add *')
    os.system(f'git commit -m "v{cli_version}"')


    # return_pyupl = os.system('pyupdater upload --service scp')

# if return_build == return_pypkg == return_pyign == return_pyupl == 0:
#     print('all good')

