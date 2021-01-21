import configparser
import getpass
import glob
import os
import pathlib
import platform
import re
import socket
import sys
import threading
import time

import loguru
import psutil
import requests
from cursor import cursor


class CFG:

    def __init__(self):

        self.cfg_gen = None
        self.cfg_net = None
        self.cfg_log = None
        self.cfg_dbg = None
        self.cfg_ftp = None
        self.cfg_pyu = None
        self.cfg_dir = None
        self.cfg_cfg = None

        self.clog_files = None

        self.game_version = None
        self.game_install_path = None
        self.game_settings_path = None
        self.game_settings_file = None
        self.tacx_settings_file = None

        self.players_sys = platform.system()
        self.players_uid = getpass.getuser()
        self.players_cid = socket.gethostname()
        self.players_arc = platform.architecture()

        self.cp = configparser.ConfigParser()

        self.game_install_path = self.get_war_path()

        if self.players_sys == "Darwin":
            wargame_cfg = 'My Games/WarThunder'
        elif self.players_sys == "Linux":
            wargame_cfg = '.config/WarThunder'
        elif self.players_sys == "Windows":
            wargame_cfg = 'Documents/My Games/WarThunder'
        else:
            wargame_cfg = None

        self.config_file_name = "thundertac.ini"

        self.game_settings_path = pathlib.Path.home().joinpath(wargame_cfg)

        if not self.game_settings_path.is_dir():
            self.game_settings_path.mkdir(mode=0o777, parents=True, exist_ok=False)

        self.tacx_settings_file = self.game_settings_path.joinpath(self.config_file_name)

        if self.game_install_path is not None:
            self.i18n = self.aces_language().replace('"', '')

        # create thundertac.ini if not exist
        if not self.tacx_settings_file.exists():
            self.create_cfg()

        self.read_cfg()

    def create_cfg(self):
        d = {
            # TODO: CHECK PATH TO LINUX GAME LOGS FOLDER
            'Linux': self.game_settings_path.joinpath('.game_logs/'),
            'Windows': pathlib.Path(self.game_install_path).joinpath('.game_logs/')
        }
        path_war_clogdir = d[platform.system()]
        self.clog_files = glob.glob(f"{str(path_war_clogdir)}/*.clog")
        while True:
            user_alias_data = self.get_user_alias()
            try:
                user_alias = user_alias_data[0]
                user_gid = user_alias_data[1]
            except TypeError:
                self.clog_files.pop()
            else:
                break

        self.cp['network'] = {}
        self.cp['general'] = {}
        self.cp['loguru'] = {}
        self.cp['debug'] = {}
        self.cp['ftpcred'] = {}
        self.cp['pyupdater'] = {}
        self.cp['path'] = {}
        self.cp['configinit'] = {}

        self.cp['network']['net_host'] = "127.0.0.1"  # self.players_cid
        self.cp['network']['net_port'] = "8111"
        self.cp['general']['ttac_usr'] = user_alias
        self.cp['general']['ttac_mas'] = user_alias
        self.cp['general']['ttac_rec'] = "ttac.rec"
        self.cp['general']['ttac_int'] = "0.02"
        self.cp['general']['user_gid'] = user_gid
        self.cp['general']['war_lang'] = self.i18n[:-1]
        self.cp['loguru']['logger_l'] = "DEBUG"
        self.cp['debug']['debug_on'] = "True"
        self.cp['ftpcred']['ftp_send'] = "False"
        self.cp['ftpcred']['ftp_addr'] = "ftp.thundertac.altervista.org"
        self.cp['ftpcred']['ftp_user'] = "thundertac"
        self.cp['ftpcred']['ftp_pass'] = "c63sghaFEP58"
        self.cp['ftpcred']['ftp_sess'] = "WIP"
        self.cp['pyupdater']['pyu_uchn'] = "stable"
        self.cp['pyupdater']['pyu_schn'] = "True"
        self.cp['path']['war_path'] = self.game_install_path.__str__()
        self.cp['path']['cfg_root'] = self.game_settings_path.__str__()
        self.cp['configinit']['init_run'] = "True"

        with open(self.tacx_settings_file, 'w') as f:
            self.cp.write(f)

    def read_cfg(self):
        self.cp.read(self.tacx_settings_file)

        # self.game_install_path = self.cp['path']['war_path']
        # for section_title, section_values in (dict(self.cp.items())).items():
        #     print(dict(section_values))

        self.cfg_net = dict(self.cp.items('network'))
        self.cfg_gen = dict(self.cp.items('general'))
        self.cfg_log = dict(self.cp.items('loguru'))
        self.cfg_dbg = dict(self.cp.items('debug'))
        self.cfg_ftp = dict(self.cp.items('ftpcred'))
        self.cfg_pyu = dict(self.cp.items('pyupdater'))
        self.cfg_dir = dict(self.cp.items('path'))
        self.cfg_cfg = dict(self.cp.items('configinit'))

    def get_war_path(self):

        try:
            self.game_install_path = pathlib.Path(self.cfg_dir['war_path'])
            self.game_settings_file = self.game_install_path.joinpath('config.blk')
            if self.game_settings_file.is_file():
                return
        except TypeError:
            cursor.hide()
        while self.game_install_path is None:
            try:
                platform_lookup = {"Darwin": "aces", "Linux": "aces", "Windows": "aces.exe"}
                target = platform_lookup[self.players_sys]
                pid_list = [pid.pid for pid in psutil.process_iter() if pid.name() == target]
                if 0 < len(pid_list):
                    proc = pathlib.Path((psutil.Process(pid_list[0])).exe())
                    self.game_install_path = proc.parent.parent
                    return self.game_install_path
                else:
                    with Spinner():
                        time.sleep(1.75)
            except KeyboardInterrupt:
                cursor.show()
                sys.exit()

    def get_game_version(self):
        if self.game_install_path:
            version_file = self.game_install_path.joinpath('content/pkg_main.ver')
            with open(version_file, "r") as frv:
                self.game_version = frv.read()
                return self.game_version

    def get_user_alias(self):

        def un_xor(data):

            xor_key = bytearray(b"\x82\x87\x97\x40\x8D\x8B\x46\x0B\xBB\x73\x94\x03\xE5\xB3\x83\x53"
                                b"\x69\x6B\x83\xDA\x95\xAF\x4A\x23\x87\xE5\x97\xAC\x24\x58\xAF\x36"
                                b"\x4E\xE1\x5A\xF9\xF1\x01\x4B\xB1\xAD\xB6\x4C\x4C\xFA\x74\x28\x69"
                                b"\xC2\x8B\x11\x17\xD5\xB6\x47\xCE\xB3\xB7\xCD\x55\xFE\xF9\xC1\x24"
                                b"\xFF\xAE\x90\x2E\x49\x6C\x4E\x09\x92\x81\x4E\x67\xBC\x6B\x9C\xDE"
                                b"\xB1\x0F\x68\xBA\x8B\x80\x44\x05\x87\x5E\xF3\x4E\xFE\x09\x97\x32"
                                b"\xC0\xAD\x9F\xE9\xBB\xFD\x4D\x06\x91\x50\x89\x6E\xE0\xE8\xEE\x99"
                                b"\x53\x00\x3C\xA6\xB8\x22\x41\x32\xB1\xBD\xF5\x28\x50\xE0\x72\xAE")

            d_data = bytearray(len(data))
            key_length = len(xor_key)
            for i, c in enumerate(data):
                d_data[i] = c ^ xor_key[(i % key_length)]
                # sys.stdout.write(chr(d_data[i]))
                # print(chr(c))
                # time.sleep(0.001)
            return d_data

        last_clog_fileis = max(self.clog_files, key=os.path.getctime)

        with open(last_clog_fileis, 'rb') as f:
            xor_ed = f.read()

        xor_ed_byte_array = bytearray(xor_ed)
        un_xor_ed = un_xor(xor_ed_byte_array)

        result = None
        if self.players_sys == "Darwin":
            pass
        elif self.players_sys == "Linux":
            import cchardet as chardet
            result = chardet.detect(bytes(un_xor_ed))
            result = result['encoding']
        elif self.players_sys == "Windows":
            result = 'ANSI'
        try:
            text_curr = bytes(un_xor_ed).decode(result)
            # with open('unxored', 'w', encoding='utf-8') as f:
            #     f.write(text_curr)
            xxx = re.search(r"(\w+)\[(\d+)] successfully passed yuplay authorization", text_curr, re.M)
            if xxx:
                print(xxx.groups())
                user_alias, user_gj_id = xxx.group(1), xxx.group(2)
                return user_alias, user_gj_id

        except LookupError as err_lookup_err_cfg_xor_decryption:
            loguru.logger.exception(err_lookup_err_cfg_xor_decryption)
            sys.exit()

    def aces_language(self):
        path_config_blk = self.game_install_path.joinpath('config.blk')
        with open(path_config_blk) as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('language'):
                return line.split(':t=')[1]


class API(CFG):

    # TODO: INHERIT FRO CFG INSTEAD OF CREATING INSTANCE OF CFG

    def __init__(self, port=8111):
        super().__init__()
        base_address = f"http://{self.players_cid}:{port}"
        self.LMAP = f"{base_address}/map.img"
        self.INFO = f"{base_address}/map_info.json"
        self.STAT = f"{base_address}/state"
        self.INDI = f"{base_address}/indicators"
        self.OBJT = f"{base_address}/map_obj.json"
        self.CHAT = f"{base_address}/gamechat"
        self.HMSG = f"{base_address}/hudmsg"

    def gamechat(self, lastId=0):
        data = requests.get(f'{self.CHAT}?lastId={lastId}').json()[-1]
        print(data)


class Spinner:
    busy = False
    delay = 0.01

    @staticmethod
    def spinning_cursor():

        while True:
            s = "LOADING...    "
            spinner_list = []
            for s_index, s_value in enumerate(s):
                s_prefix = 11
                s_suffix = 0 + s_index

                for j, jj in enumerate(s):
                    if (s_index + j) <= len(s):
                        spinner_list.append(s[0:s_index] + " "*(s_prefix-s_index) + s_value + " "*s_suffix)
                        s_prefix -= 1
                        s_suffix += 1

            for cursor_iteration in spinner_list:  # '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏':
                yield cursor_iteration

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\r')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


if __name__ == '__main__':
    pass
    # print(b.gamechat())

# class UserInfo:
#
#     def __init__(self):
#
#         self.game_install_path = None
#
#         self.config_file_name = "thundertac.ini"
#         cp = configparser.ConfigParser()
#
#         self.players_sys = platform.system()
#         self.players_uid = getpass.getuser()
#         self.players_cid = socket.gethostname()
#         self.players_arc = platform.architecture()
#
#         if self.players_sys == "Darwin":
#             # self.players_uid = "MAC SUPPORT LIMITED - HELP NEEDED"
#             self.wargame_cfg = 'My Games/WarThunder'
#
#         elif self.players_sys == "Linux":
#             # self.players_uid = os.getenv('USER')
#             self.wargame_cfg = '.config/WarThunder'
#
#         elif self.players_sys == "Windows":
#             # self.players_uid = os.getenv('USERNAME')
#             self.wargame_cfg = 'Documents/My Games/WarThunder'
#
#         self.game_settings_path = pathlib.Path.home().joinpath(self.wargame_cfg)
#         self.tacx_settings_file = self.game_settings_path.joinpath(self.config_file_name)
#
#         self.wargame_dir_known = False
#
#         self.game_install_path = self.get_game_root_dir()
#
#         # cp.read(self.tacx_settings_file)
#         # if cp.has_section('path'):
#         #     if pathlib.Path(cp['path']['war_path']).exists():
#         #         self.game_install_path = pathlib.Path(cp['path']['war_path'])
#         # if self.game_install_path == "":
#         #     self.game_install_path = self.get_game_root_dir()
#         #     cp['path']['war_path'] = str(self.game_install_path)
#         #     with open(self.tacx_settings_file, 'w') as f:
#         #         cp.write(f)
#
#     def get_game_root_dir(self):
#         platform_lookup = {"Windows": "aces.exe", "Linux": "aces"}
#         for pid in psutil.pids():
#             psutil.Process(pid).name()
#             if psutil.Process(pid).name() == platform_lookup[self.players_sys]:
#                 aces_pid = pid
#                 p = psutil.Process(aces_pid)
#                 game_path_exe = pathlib.Path(p.exe())
#                 self.game_install_path = game_path_exe.parent.parent
#                 self.wargame_dir_known = True
#                 return self.game_install_path
#
#     def get_game_version(self):
#         if not self.wargame_dir_known:
#             self.get_game_root_dir()
#         if self.wargame_dir_known:
#             version_file = self.game_install_path.joinpath('content/pkg_main.ver')
#             with open(version_file, "r") as frv:
#                 return frv.read()
#
#     def aces_language(self):
#         path_config_blk = self.game_install_path.joinpath('config.blk')
#         with open(path_config_blk) as f:
#             lines = f.readlines()
#         for line in lines:
#             if line.startswith('language'):
#                 return line.split(':t=')[1]
