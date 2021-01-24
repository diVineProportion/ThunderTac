import argparse
import os
import pathlib
import re
import subprocess
import sys
import time

import __init__

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
    print(f'current version: {__init__.__version__}')
    client_version = input(f'{{major}}.{{minor}}.{{patch}}.{{channel}}.{{release}}: ')

    with open('__init__.py', 'w') as f:
        f.write(f'__version__ = "{client_version}"')

    # if channel == ("0" or ""):
    #     channel = ""
    # if channel == ("1" or "a" or "alpha"):
    #     channel = "alpha"
    # if channel == ("2" or "b" or "beta"):
    #     channel = "beta"

    os.system(f'pyupdater build --app-version={client_version} --pyinstaller-log-info win.spec')
    os.system(f'pyupdater pkg --process')
    os.system(f'pyupdater pkg --sign')

    # return_pyupl = os.system('pyupdater upload --service scp')

# if return_build == return_pypkg == return_pyign == return_pyupl == 0:
#     print('all good')

