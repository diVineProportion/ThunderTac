import platform
import time
import locale
import ctypes
from os import environ
from os.path import join


def information_gathering(developer=False):
    """various information gathering for """
    if developer:
        # python information
        version = platform.python_version()
        version_tuple = platform.python_version_tuple()
        compiler = platform.python_compiler()
        build = platform.python_build()

    # system information
    system = platform.system()
    node = platform.node()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    architecture = platform.architecture()

    # localization information
    timezone = time.tzname[time.localtime().tm_isdst]
    codepage = locale.getdefaultlocale()[1]
    localeui = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]

    return system, architecture[0]


class UserInformation:
    def __init__(self):
        self.WT_USER_DIR = "{}\\Documents\\My Games\\WarThunder\\Saves\\".format(environ['USERPROFILE'])
        self.last_login = self.last_login.split('=')[1].replace('\n', '')
        self.machine_id = self.machine_id.split('"')[1]

    def get_unique_id(self):
        last_login_path = self.WT_USER_DIR + "lastlogin.blk"
        with open(last_login_path, 'r') as llpfr:
            self.last_login = llpfr.readline()

    def get_machine_id(self):
        machine_id_path = join(self.WT_USER_DIR, self.last_login, 'production\\machine.blk')
        with open(machine_id_path, 'r') as f:
            self.machine_id = f.read()
        self.machine_id = self.machine_id.split('\n')
        for line_no, line_val in enumerate(self.machine_id):
            if line_no == 3:
                self.machine_id = line_val


if __name__ == "__main__":
    pass
