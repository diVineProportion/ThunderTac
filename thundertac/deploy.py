import os

import __init__

if __name__ == "__main__":
    CURR_APP_VERSION = __init__.__version__
    print(f'current version: {CURR_APP_VERSION}')
    NEW_APP_VERSION = input(f'{CURR_APP_VERSION} --> ?: ')

    with open('__init__.py', 'w') as f:
        f.write(f'__version__ = "{NEW_APP_VERSION}"')


    os.system(f'pyupdater build --app-version={NEW_APP_VERSION} --pyinstaller-log-info pyu_cfg\win.spec')
    os.system(f'pyupdater pkg --process')
    os.system(f'pyupdater pkg --sign')
    os.system('pyupdater upload --service scp')