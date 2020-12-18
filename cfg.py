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

        self.wargame_dir = None
        self.game_version = None

        self.config_file = "thundertac.ini"

        self.players_sys = platform.system()
        self.players_uid = getpass.getuser()
        self.players_cid = socket.gethostname()
        self.players_arc = platform.architecture()

        self.cp = configparser.ConfigParser()

        if self.players_sys == "Darwin":
            self.wargame_cfg = 'My Games/WarThunder'

        elif self.players_sys == "Linux":
            self.wargame_cfg = '.config/WarThunder'

        elif self.players_sys == "Windows":
            self.wargame_cfg = 'Documents/My Games/WarThunder'

        self.config_root = pathlib.Path.home().joinpath(self.wargame_cfg)
        self.config_path = self.config_root.joinpath(self.config_file)

        if not self.config_path.exists():
            self.create_cfg()

        self.read_cfg()

        # if self.wargame_dir:
        #     self.get_war_path()

    def create_cfg(self):

        user_alias, user_gid = self.get_user_alias()
        # get_war_path() returns a pathlib object
        war_path = self.get_war_path().__str__()
        cfg_root = str(self.config_root)
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
        self.cp['loguru']['logger_l'] = "DEBUG"
        self.cp['debug']['debug_on'] = "True"
        self.cp['ftpcred']['ftp_send'] = "False"
        self.cp['ftpcred']['ftp_addr'] = "ftp.thundertac.altervista.org"
        self.cp['ftpcred']['ftp_user'] = "thundertac"
        self.cp['ftpcred']['ftp_pass'] = "c63sghaFEP58"
        self.cp['ftpcred']['ftp_sess'] = "WIP"
        self.cp['pyupdater']['pyu_uchn'] = "stable"
        self.cp['pyupdater']['pyu_schn'] = "True"
        self.cp['path']['war_path'] = war_path
        self.cp['path']['cfg_root'] = cfg_root
        self.cp['configinit']['init_run'] = "True"


        with open(self.config_path, 'w') as f:
            self.cp.write(f)

    def read_cfg(self):

        self.cp.read(self.config_path)

        # self.wargame_dir = self.cp['path']['war_path']
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
        platform_lookup = {"Darwin": "aces", "Linux": "aces", "Windows": "aces.exe"}
        target = platform_lookup[self.players_sys]
        cursor.hide()
        while self.wargame_dir is None:
            try:
                pid_list = [pid.pid for pid in psutil.process_iter() if pid.name() == target]
                if 0 < len(pid_list):
                    proc = pathlib.Path((psutil.Process(pid_list[0])).exe())
                    wargame_dir = proc.parent.parent
                    # loguru.logger.log("PILOT", f"{self.wargame_dir}")
                    return wargame_dir
                else:
                    with Spinner():
                        time.sleep(5)
            except KeyboardInterrupt:
                cursor.show()
                sys.exit()


    def get_game_version(self):
        if self.wargame_dir:
            version_file = self.wargame_dir.joinpath('content/pkg_main.ver')
            with open(version_file, "r") as frv:
                self.game_version = frv.read()
                # self.loguru.logger.log("PILOT", f"{self.game_version}")
                return self.game_version

    def get_user_alias(self):

        def unxor(data):

            XOR_KEY = bytearray(b"\x82\x87\x97\x40\x8D\x8B\x46\x0B\xBB\x73\x94\x03\xE5\xB3\x83\x53"
                                b"\x69\x6B\x83\xDA\x95\xAF\x4A\x23\x87\xE5\x97\xAC\x24\x58\xAF\x36"
                                b"\x4E\xE1\x5A\xF9\xF1\x01\x4B\xB1\xAD\xB6\x4C\x4C\xFA\x74\x28\x69"
                                b"\xC2\x8B\x11\x17\xD5\xB6\x47\xCE\xB3\xB7\xCD\x55\xFE\xF9\xC1\x24"
                                b"\xFF\xAE\x90\x2E\x49\x6C\x4E\x09\x92\x81\x4E\x67\xBC\x6B\x9C\xDE"
                                b"\xB1\x0F\x68\xBA\x8B\x80\x44\x05\x87\x5E\xF3\x4E\xFE\x09\x97\x32"
                                b"\xC0\xAD\x9F\xE9\xBB\xFD\x4D\x06\x91\x50\x89\x6E\xE0\xE8\xEE\x99"
                                b"\x53\x00\x3C\xA6\xB8\x22\x41\x32\xB1\xBD\xF5\x28\x50\xE0\x72\xAE")

            d_data = bytearray(len(data))
            key_length = len(XOR_KEY)
            for i, c in enumerate(data):
                d_data[i] = c ^ XOR_KEY[(i % key_length)]
            return d_data

        self.warpath_dir = self.get_war_path()
        # TODO: MERGE DICT (d) with PATHS FROM CFG INIT (wargame_cfg)
        d = {
            # TODO: CHECK PATH TO LINUX GAME LOGS FOLDER
            'Linux': self.config_root.joinpath('.game_logs/'),
            'Windows': self.warpath_dir.joinpath('.game_logs/')
        }

        path_war_clogdir = d[platform.system()]
        temp = f"{str(path_war_clogdir)}/*.clog"
        last_clog_fileis = max((glob.glob(temp)), key=os.path.getctime)

        with open(last_clog_fileis, 'rb') as f:
            xored = f.read()
            xored_byte_array = bytearray(xored)
            unxored = unxor(xored_byte_array)
            import cchardet as chardet
            result = chardet.detect(bytes(unxored))
            try:
                text_curr = bytes(unxored).decode(result['encoding'])
                # with open('unxored.txt', 'w', encoding=result['encoding']) as f:
            #     f.write(text_curr)
            except LookupError:
                print('IF THIS IS THE FIRST TIME RUNNING THUNDERTAC, PLEASE JOIN & LEAVE A CUSTOM BATTLE, THEN RESTART')
                sys.exit()
            xxx = re.search(r"(\w+)\[(\d+)\] successfully passed yuplay authorization",
                            text_curr,
                            re.MULTILINE)
            if xxx:
                print(xxx.groups())
                user_alias, user_gj_id = xxx.group(1), xxx.group(2)
                return user_alias, user_gj_id


    def inspector(self, message=""):
        pass
        import inspect
        _ = inspect.stack()
        path_full = _[1][1]
        from_line = _[1][2]
        from_modu = _[1][3]
        name_file = path_full.split("thundertac")[-1]
        # loguru.logger.log("PILOT", f"{name_file}:{from_modu}:{from_line} | {message}")

class API():
    BASE = None
    # TODO: INHERIT FRO CFG INSTEAD OF CREATING INSTANCE OF CFG

    def __init__(self):

        from_cfg = CFG()

        host = from_cfg.cfg_net['net_host']
        port = from_cfg.cfg_net['net_port']
        BASE = f"http://{host}:{port}"
        self.LMAP = f"{BASE}/map.img"
        self.INFO = f"{BASE}/map_info.json"
        self.STAT = f"{BASE}/state"
        self.INDI = f"{BASE}/indicators"
        self.OBJT = f"{BASE}/map_obj.json"
        self.CHAT = f"{BASE}/gamechat"
        self.HMSG = f"{BASE}/hudmsg"

    def gamechat(self, lastId=0):
        data = requests.get(f'{self.CHAT}?lastId={lastId}').json()[-1]
        print(data)

class Spinner:
    busy = False
    delay = 0.01

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏':
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

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
    a = CFG()
    b = API()
    print(dir(a))
    print(a.get_war_path())
    # print(b.gamechat())




# class UserInfo:
#
#     def __init__(self):
#
#         self.wargame_dir = None
#
#         self.config_file = "thundertac.ini"
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
#         self.config_root = pathlib.Path.home().joinpath(self.wargame_cfg)
#         self.config_path = self.config_root.joinpath(self.config_file)
#
#         self.wargame_dir_known = False
#
#         self.wargame_dir = self.get_game_root_dir()
#
#         # cp.read(self.config_path)
#         # if cp.has_section('path'):
#         #     if pathlib.Path(cp['path']['war_path']).exists():
#         #         self.wargame_dir = pathlib.Path(cp['path']['war_path'])
#         # if self.wargame_dir == "":
#         #     self.wargame_dir = self.get_game_root_dir()
#         #     cp['path']['war_path'] = str(self.wargame_dir)
#         #     with open(self.config_path, 'w') as f:
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
#                 self.wargame_dir = game_path_exe.parent.parent
#                 self.wargame_dir_known = True
#                 return self.wargame_dir
#
#     def get_game_version(self):
#         if not self.wargame_dir_known:
#             self.get_game_root_dir()
#         if self.wargame_dir_known:
#             version_file = self.wargame_dir.joinpath('content/pkg_main.ver')
#             with open(version_file, "r") as frv:
#                 return frv.read()
#
#     def aces_language(self):
#         path_config_blk = self.wargame_dir.joinpath('config.blk')
#         with open(path_config_blk) as f:
#             lines = f.readlines()
#         for line in lines:
#             if line.startswith('language'):
#                 return line.split(':t=')[1]
