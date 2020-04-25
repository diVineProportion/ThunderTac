import os
import sys
import winreg
from pprint import pprint

from pyupdater.client import Client
from client_config import ClientConfig


keyVal = "SOFTWARE\\WarThunderApps\\ThunderTac"
config_file = "config.ini"
config_root = f"{os.environ['LOCALAPPDATA']}\\WarThunderApps\\ThunderTac"
config_path = f"{config_root}\\{config_file}"


def read_registry():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        winreg.OpenKey(registry, keyVal)
    except FileNotFoundError:
        write_registry("0.0.0.0.0")
    finally:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        raw_key = winreg.OpenKey(registry, keyVal)
        i = 0
        while 1:
            name, value, _type = winreg.EnumValue(raw_key, i)
            i += 1
            return value


def write_registry(registry_string):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)

    winreg.SetValueEx(key, "Version ", 0, winreg.REG_SZ, registry_string)
    winreg.CloseKey(key)


def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)


def initialization(_channel, _preferred_channel, _is_strict):
    client = Client(ClientConfig())
    client.refresh()

    client.add_progress_hook(print_status_info)

    app_name = ClientConfig.APP_NAME
    app_version = read_registry()

    return client.update_check(app_name, app_version, channel=_preferred_channel, strict=_is_strict)


def get_archive_information(current):
    try:
        current = current.split('-')[2].replace('.zip', '')
        channel_letter = current[-1]
        if channel_letter == "a":
            return current.split('a')[0], "alpha"
        elif channel_letter == "b":
            return current.split('b')[0], "beta"
        else:
            return "stable"
    except AttributeError:
        pass


def update_check(_app_update, _verbose=False):
    global displayed_version
    if _app_update is not None:
        try:
            current_version, current_channel = get_archive_information(_app_update._current_archive_name)

            if not displayed_version:
                print(f"THIS VERSION: {_app_update.app_name} v{current_version} ({current_channel}) ")
                displayed_version = True
            print(f"There is an update available on the '{_app_update.channel}' channel")
            if _verbose:
                pprint(vars(_app_update))
        except TypeError:
            pass
        except UnboundLocalError:
            pass


def perform_update(_app_update):
    if _app_update is not None:
        _app_update.download()
        if _app_update.is_downloaded():
            write_registry(app_update.latest)
        if _app_update.is_downloaded():
            _app_update.extract_restart()


def get_clients_channel():
    from config import cfg_pyupdater
    return cfg_pyupdater()


channels = ['alpha', 'beta', 'stable']
displayed_version = False

for channel in channels:

    if __name__ == "_update_":

        if getattr(sys, 'frozen', False):
            preferred_channel, is_strict = get_clients_channel()
            app_update = initialization(channel, preferred_channel, is_strict)
            update_check(app_update)
            perform_update(app_update)

        elif __file__:
            # FIXME: BROKEN
            preferred_channel, is_strict = get_clients_channel()
            app_update = initialization(channel, preferred_channel, is_strict)
            update_check(app_update)

    elif __name__ == "__main__":
        preferred_channel, is_strict = get_clients_channel()
        app_update = initialization(channel, preferred_channel, is_strict)
        update_check(app_update)
