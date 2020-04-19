import ctypes
import getpass
import locale
import os
import pathlib
import platform
import time
import winreg

import loguru


def get_basic_info():
    players_uid = getpass.getuser()
    players_cid = os.getenv('COMPUTERNAME')
    return players_uid, players_cid


def get_ver_info():
    """ get steam install directory from registry; use found path to read .ttacver file """
    if platform.system() == 'Windows':
        list_possibilities = [
            [winreg.HKEY_CURRENT_USER, "SOFTWARE\\Gaijin\\WarThunder\\InstallPath"],
            [winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Valve\\Steam\\InstallPath"],
            [winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Valve\\Steam\\InstallPath"],
        ]
        for list_item in list_possibilities:
            hkey, reg_path = list_item[0], list_item[1]
            path, name = os.path.split(reg_path)
            try:
                with winreg.OpenKey(hkey, path) as key:
                    pre_path = winreg.QueryValueEx(key, name)[0]
                    if "Steam" in path:
                        pre_path = "{}\\SteamApps\\common\\War Thunder".format(pre_path)
                    post_path = "content\\pkg_main.ver"
                    version_file = os.path.join(pre_path, post_path)
                    with open(version_file, "r") as frv:
                        return frv.read()
            except FileNotFoundError as err_ver_not_found:
                loguru.logger.debug(str(err_ver_not_found) + " key: {}".format(key))
                continue


def localization_info():
    """ gathers various non-sensitive bits of localization information """
    time_zone = time.tzname[time.localtime().tm_isdst]
    code_page = locale.getdefaultlocale()[1]
    locale_ui = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
    return time_zone, locale_ui

    # project contributor information
    # if contributor:
    #     # python information
    #     .ttacver = platform.python_version()
    #     version_tuple = platform.python_version_tuple()
    #     compiler = platform.python_compiler()
    #     build = platform.python_build()


def system_info():
    """ gathers various non-sensitive bits of system information """
    system = platform.system()
    node = platform.node()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    architecture = platform.architecture()
    return system


class UserInformation:
    def __init__(self, ):
        """ init & os platform detection """
        self.path = None
        self.last_login = None
        self.machine_id = None
        self.operating_system = platform.system()
        if self.operating_system == "Darwin":
            pass
        elif self.operating_system == "Linux":
            path = '.config/WarThunder/Saves/'
        elif self.operating_system == "Windows":
            path = 'Documents/My Games/WarThunder/Saves/'

        self.path_userspace = pathlib.Path.home().joinpath(path)

    def get_lastlogin(self):
        """ get last uid (unique_id) logged in """
        last_login_path = self.path_userspace.joinpath("lastlogin.blk")
        with open(last_login_path, 'r') as f:
            self.last_login = f.readline()
        self.last_login = self.last_login.split('=')[1].replace('\n', '')
        return self.last_login

    def get_machine_id(self):
        """ get machine_id for last uid (unique_id) """
        machine_id_path = os.path.join(self.path_userspace, self.last_login, 'production\\machine.blk')
        with open(machine_id_path, 'r') as f:
            self.machine_id = f.read()
        self.machine_id = self.machine_id.split('\n')
        for line_no, line_val in enumerate(self.machine_id):
            if line_no == 3:
                self.machine_id = line_val.split('"')[1]
        return self.machine_id


if __name__ == "__main__":
    print(get_basic_info())
    print(get_ver_info())
    print(localization_info())
    print(system_info())