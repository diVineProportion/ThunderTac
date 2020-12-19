# import snoop

user_sesid = ''
time_isset = ''

class State:
    class Recorder:
        active = ''

# @snoop()
def main_fun():
    global user_sesid
    global time_isset

    ## built in imports
    import collections
    import configparser
    import ftplib
    import glob
    import math
    import os
    import pathlib
    import pprint
    import random
    import re
    import sys
    import time
    import zipfile

    from signal import signal, SIGINT

    ## 3rd party imports
    import arrow
    import loguru
    import ntplib
    import paho.mqtt.client as mqtt
    import platform
    import psutil
    import requests
    import simplejson
    import simplejson as json

    from mega import Mega
    from requests.exceptions import RequestException

    ## local imports
    ##### import config
    # import _update_
    ##### import arguments
    # import map_info
    ##### import userinfo

    import map_info
    ##### from config import cfc_general
    ##### from config import cfg_loguru
    ##### from config import cfg_debug
    ##### from config import cfg_ftpcred
    ##### from config import cfg_configinit
    ##### from config import WebInterfaceEndpoints as WebAPI

    windows = linux = darwin = False

    ##### init_run = cfg_configinit()

    ##### if init_run:
    #####     import ascii_config

    ##### ttac_usr, ttac_mas, ttac_rec, ttac_int = cfc_general()
    ##### logger_l = cfg_loguru()
    ##### # debug_on = cfg_debug()
    ##### ftp_send, ftp_addr, ftp_user, ftp_pass, ftp_sess = cfg_ftpcred()
    ##### debug_on = True

    import cfg
    config1 = cfg.CFG()

    net_host = config1.cfg_net['net_host']
    net_port = config1.cfg_net['net_port']
    ttac_usr = config1.cfg_gen['ttac_usr']
    ttac_mas = config1.cfg_gen['ttac_mas']
    ttac_rec = config1.cfg_gen['ttac_rec']
    ttac_int = config1.cfg_gen['ttac_int']
    user_gid = config1.cfg_gen['user_gid']
    logger_l = config1.cfg_log['logger_l']
    debug_on = config1.cfg_dbg['debug_on']
    ftp_send = config1.cfg_ftp['ftp_send']
    ftp_addr = config1.cfg_ftp['ftp_addr']
    ftp_user = config1.cfg_ftp['ftp_user']
    ftp_pass = config1.cfg_ftp['ftp_pass']
    init_run = config1.cfg_cfg['init_run']
    war_path = config1.cfg_dir['war_path']
    cfg_root = config1.cfg_dir['cfg_root']

    cp = configparser.ConfigParser()
    cp.read(config1.config_path)
    init_run = cp['configinit'].getboolean('init_run')
    debug_on = cp['debug'].getboolean('debug_on')

    loguru.logger.remove()
    loguru.logger.add(sys.stderr, level=logger_l)

    CONVTO_MPS = 0.277778

    # TODO: CLEAN THIS GARBAGE UP
    filename = ""
    time_rec_start = None
    rec_start_mode_gamechat = True
    map_objects = None
    # TODO: write function to automatically handle this; start false, set true individually, then reset at appropriate time.
    player_fetch_fail = None
    x = y = z = r = p = h = None
    ias = player = lati_m = long_m = None
    unit = s_throttle1 = tas = fuel_kg = None
    m = aoa = fuel_vol = gear = flaps = None
    stick_ailerons = stick_elevator = None
    ind = sta = None

    # __import__('ipdb').set_trace(context=9)
    # ipdb.set_trace(context=21)

    re_get_sesid = re.compile(r'[\d]+\.[\d]+ \[D\]  '
                              r'AcesMpContext: '
                              r'onJoinMatch : '
                              r'sessionId:([a-f0-9]+)', re.I | re.M)
    re_get_teams = re.compile(r"[\d]+\.[\d]+ "
                              r"MULP onStateChanged\(\) "
                              r"MULP p(?P<p>[\d]{1,2}) "
                              r"n='(?P<nick>.*)' "
                              r"(?P<s0>[A-Z_]+)->(?P<s1>[A-Z_]+) "
                              r"t=(?P<t>[0-2]) "
                              r"c=(?P<c>[0-9]) "
                              r"f=(?P<f>[\d]+)\(l=(?P<l>[\d])\) "
                              r"mid=(?P<mid>[\d]+) "
                              r"uid=(?P<uid>[\d]+) "
                              r"u=(?P<u>0x[0-9a-f]+/[0-9A-F]+)", re.I | re.M)

    XOR_KEY = bytearray(b"\x82\x87\x97\x40\x8D\x8B\x46\x0B\xBB\x73\x94\x03\xE5\xB3\x83\x53"
                        b"\x69\x6B\x83\xDA\x95\xAF\x4A\x23\x87\xE5\x97\xAC\x24\x58\xAF\x36"
                        b"\x4E\xE1\x5A\xF9\xF1\x01\x4B\xB1\xAD\xB6\x4C\x4C\xFA\x74\x28\x69"
                        b"\xC2\x8B\x11\x17\xD5\xB6\x47\xCE\xB3\xB7\xCD\x55\xFE\xF9\xC1\x24"
                        b"\xFF\xAE\x90\x2E\x49\x6C\x4E\x09\x92\x81\x4E\x67\xBC\x6B\x9C\xDE"
                        b"\xB1\x0F\x68\xBA\x8B\x80\x44\x05\x87\x5E\xF3\x4E\xFE\x09\x97\x32"
                        b"\xC0\xAD\x9F\xE9\xBB\xFD\x4D\x06\x91\x50\x89\x6E\xE0\xE8\xEE\x99"
                        b"\x53\x00\x3C\xA6\xB8\x22\x41\x32\xB1\xBD\xF5\x28\x50\xE0\x72\xAE")

    platform_data = {
        'Darwin': {
            'path': 'My Games/WarThunder',
            'name': 'aces'
        },
        'Linux': {
            'path': '.config/WarThunder',
            'name': 'aces'
        },
        'Windows': {
            'path': 'Documents/My Games/WarThunder',
            'name': 'aces.exe'
        }
    }

    def check_for_aces(procs):
        if findProcIdByName(procs):
            return True
        else:
            print('aces not running:', True)
            return False

    def checkIfProcessRunning(processName):
        for proc in psutil.process_iter():
            try:
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def findProcIdByName(processName):
        listOfProcessObjects = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time', 'exe'])
                if processName.lower() in pinfo['name'].lower():
                    listOfProcessObjects.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return listOfProcessObjects

    def war_file_reader(war_file):
        with open(war_file) as f:
            if war_file.suffix == ".ver":
                return f.read()
            elif war_file.suffix == ".blk":
                _ = [x for x in f.readlines() if x.startswith('language')][0]
                return _.split(':t=')[1][1:-2]

    def unxor(data):
        d_data = bytearray(len(data))
        key_length = len(XOR_KEY)
        for i, c in enumerate(data):
            d_data[i] = c ^ XOR_KEY[(i % key_length)]
        return d_data

    def get_user_alias(text):
        for idx_line, text_line in enumerate(text):
            xxx = re.search(r"[\d]+\.[\d]+\s\[D\]\s\s\$07\s(\w+)\[(\d+)\] successfully passed yuplay authorization",
                            text_line, re.MULTILINE)
            if xxx:
                print(xxx.groups())
                # return xxx.group(1), xxx.group(2)

    def get_user_sesid(text, _dict):
        list_tid = []
        list_sid = []
        for idx_line, text_line in enumerate(text):
            x1 = re_get_sesid.search(text_line) or None
            if x1:
                try:
                    time_elapsed = time.time() - time_start
                    session_id = x1.group(1)
                    list_sid.append(session_id)
                    list_tid.append(time_elapsed)
                    _dict[max(list_tid)] = {'session_id': list_sid[-1]}
                except AttributeError:
                    pass
        return list_sid  # _dict

    def get_users_team(text, _list_teams, alias):
        for idx_line, text_line in enumerate(text):
            x2 = re_get_teams.search(text_line) or None
            if x2 is not None:
                if x2.group(2) == alias:
                    _list_teams.append(x2.group(5))
        return _list_teams

    def init_temp_db():
        tdb = configparser.ConfigParser()
        tdb['MAP_INFO'] = {}
        tdb['HEADER_INFO'] = {}
        tdb['MAP_INFO']['map_lookup_result'] = ''
        tdb['HEADER_INFO']['utc_start_date'] = ''
        tdb['HEADER_INFO']['utc_start_time'] = ''
        tdb['HEADER_INFO']['loc_start_date'] = ''
        tdb['HEADER_INFO']['loc_start_time'] = ''
        with open('temp.ini', 'w') as f:
            tdb.write(f)
        return tdb

    def gaijin_state_method():
        """last_state.blk is created and updated live but hasn't been implemented in thundertac"""
        while True:
            _ = platform.system()
            try:
                if _ == "Darwin":
                    path_user_cfg = 'My Games/WarThunder'
                elif _ == "Linux":
                    path_user_cfg = '.config/WarThunder/Saves'
                elif _ == "Windows":
                    path_user_cfg = 'Documents/My Games/WarThunder/Saves'
                path_user_abs = pathlib.Path.home().joinpath(path_user_cfg, 'last_state.blk')
                with open(path_user_abs, 'r') as fr:
                    prev_state, last_state = fr.readlines()
                # prev_state = prev_state.split('"')[1]
                last_state = last_state.split('"')[1]
                return last_state

            except ValueError:
                pass
        # while True:
        #     try:
        #         if platform.system() == "Windows":
        #             from winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
        #             with open(os.environ['USERPROFILE'] + '\\Documents\\My Games\\WarThunder\\Saves\\last_state.blk',
        #                       'r') as fr:
        #                 prev_state, last_state = fr.readlines()
        #             # prev_state = prev_state.split('"')[1]
        #             last_state = last_state.split('"')[1]
        #             return last_state
        #         else:
        #             pass
        #             # TODO: linux and macos not yet implemented
        #     except ValueError:
        #         pass

    def get_utc_offset():
        """get difference between players local machine and NTP time server; use to sync players"""
        ntpreq = None
        wait_for_response = True
        while wait_for_response:
            try:
                ntpreq = ntp.request("pool.ntp.org")
                wait_for_response = False
            except ntplib.NTPException:
                pass
        # time offset is the difference between the users clock and the worldwide time synced NTP protocol
        time_offset = (ntpreq.recv_time - ntpreq.orig_time + ntpreq.tx_time - ntpreq.dest_time) / 2
        # record start time is the client synced UTC starting time with the offset included.
        record_start_time = str(arrow.get(arrow.utcnow().float_timestamp + time_offset))[:-6]
        return record_start_time

    def set_filename():
        """maintain file structure by reading localization information"""
        acmi_folder_path = pathlib.Path(f'./ACMI/{user_sesid}')
        if not acmi_folder_path.is_dir():
            acmi_folder_path.mkdir(mode=0o777, parents=True, exist_ok=False)
        # if not os.path.exists(f'.\\ACMI\\{user_sesid}'):
        #     os.makedirs(f'.\\ACMI\\{user_sesid}')
        sdate, stime = (str(arrow.utcnow())[:-13]).replace(":", ".").split("T")
        ldate, ltime = (str(arrow.now())[:-13]).replace(":", ".").split("T")
        # temp_db.read('temp.ini')
        # temp_db['HEADER_INFO']['utc_start_date'] = sdate
        # temp_db['HEADER_INFO']['utc_start_time'] = stime
        # temp_db['HEADER_INFO']['loc_start_date'] = ldate
        # temp_db['HEADER_INFO']['loc_start_time'] = ltime
        # with open('temp.ini', 'w') as f:
        #     temp_db.write(f)
        return f"ACMI/{user_sesid}/{sdate}_{stime}_{ttac_usr}.acmi"

    def get_web_reqs(req_type):
        """request data from web interface"""
        try:
            response = requests.get(req_type, timeout=0.1)
            if response.status_code == 200:
                return response.json()
            else:
                print(f'ERROR: {response.status_code}')
        except requests.exceptions.ReadTimeout:
            pass
        # NOTE: this is triggered when you leave a match
        except simplejson.errors.JSONDecodeError as e:
            pass

    def window_title():
        if platform.system() == "Windows":
            import win32gui
            title_hang = "War Thunder"
            title_load = "War Thunder - Loading"
            title_batt = "War Thunder - In battle"
            title_driv = "War Thunder - Test Drive"
            title_test = "War Thunder - Test Flight"
            title_wait = "War Thunder - Waiting for game"
            title_dx32 = "War Thunder (DirectX 11, 32bit) - In battle"
            """Use win32api window handle titles to detect  war thunder state"""
            # TODO: consider using xored clog file for more robust detection
            list_title = [title_hang, title_wait, title_batt, title_load, title_driv, title_test, title_dx32]
            for window_title in list_title:
                whnd = win32gui.FindWindowEx(None, None, None, window_title)
                if not (whnd == 0):
                    return window_title

        elif platform.system() == "Linux":
            try:
                import ewmh
                window_manager = ewmh.EWMH()
                title_hang = b"War Thunder (Vulkan, 64bit)"
                title_load = b"War Thunder (Vulkan, 64bit) - Loading"
                title_batt = b"War Thunder (Vulkan, 64bit) - In battle"
                title_driv = b"War Thunder (Vulkan, 64bit) - Test Drive"
                title_test = b"War Thunder (Vulkan, 64bit) - Test Flight"
                title_wait = b"War Thunder (Vulkan, 64bit) - Waiting for game"
                list_title = [title_hang, title_wait, title_batt, title_load, title_driv, title_test]

                client_list = window_manager.getClientList()
                for window in client_list:
                    # print(window_manager.getWmName(window))
                    if window_manager.getWmName(window) in list_title:
                        window_title_from_window_id = window_manager.getWmName(window)
                        return window_title_from_window_id.decode('utf-8')
            except Exception as e:
                print(e)


    def hdg(dx, dy):
        """Fallback in case compass is missing from indicators pannel"""
        dx *= long_m * -1
        dy *= lati_m * -1
        return int(180 - (180 / math.pi) * math.atan2(dx, dy))

    def parachute_down(init_altitude):
        """Control parachute decent rate"""
        # avg ROF for parachte = 20 km/h
        # 20km/1hr * 1hr/3600s * 1000m/1km = ~5.5m/1s
        # 5.5 too slow
        falltime = init_altitude * 2.5
        return falltime

    def insert_header(map_information, reference_time, alias, sesid):
        acmi_header = (
            f"FileType={'text/acmi/tacview'}\n"
            f"FileVersion={'2.1'}\n"
            f"0,DataSource=War Thunder\n"
            f"0,DataRecorder=ThunderTac\n"
            f"0,ReferenceTime={reference_time}Z\n"
            f"0,RecordingTime={str(arrow.utcnow())[:-13]}Z\n"
            f"0,Author={alias}\n"
            # f"0,Author={players_uid}@{players_cid}\n"
            f"0,Title={(window_title()[14:]).title()}: {map_information}\n"
            f"0,Category={sesid}\n"
            f"0,Briefing={'None Provided'}\n"
            f"0,Debriefing={'None Provided'}\n"
            f"0,Comments=v{str(config1.get_game_version())}\n"
            f"0,ReferenceLongitude={'0'}\n"
            f"0,ReferenceLatitude={'0'}\n"
        )

        with open(filename, "a", newline="") as f:
            f.write(acmi_header)

    def set_user_object():
        """Object ID assigner"""
        return hex(random.randint(0, int(0xFFFFFFFFFFFFFFFF)))[2:]

    def gamechat(id_msg=0):
        url_gamechat = f"{WebAPI.CHAT}?lastId={id_msg}"
        url_gamechat = url_gamechat.format(id_msg)
        req_gamechat = requests.get(url_gamechat, timeout=0.02)
        return req_gamechat.json()

    def hudmsg(lastevt=0, lastdmg=0):
        # def hudmsg(id_evt=0, id_dmg=0):
        #     url_hudmsg = f"{WebAPI.HMSG}?lastEvt={id_evt}&lastDmg={id_dmg}"
        #     url_hudmsg = url_hudmsg.format(id_evt, id_dmg)
        #     req_hudmsg = requests.get(url_hudmsg, timeout=0.02)
        #     return req_hudmsg.json()
        try:
            req = "http://localhost:8111/hudmsg?lastEvt={}&lastDmg={}"
            x = requests.get(req.format(lastevt, lastdmg), timeout=0.02).json()
            return x
        except (IndexError, requests.exceptions.ReadTimeout):
            pass

    def get_unit():
        wt_units_lookup = None
        try:
            with open('wtunits.json', 'r', encoding='utf-8') as f:
                wt_units_lookup = json.loads(f.read())
        except FileNotFoundError:
            wt_units_host = 'https://raw.githubusercontent.com/diVineProportion/ThunderTac/rewrite/wtunits.json'
            wt_units_data = requests.get(wt_units_host).json()
            wt_units_version = wt_units_data['version']
            loguru.logger.info(f"[A] UNITS LIBRARY: War Thunder v'{wt_units_version}' Loaded")
            wt_game_version = config1.get_game_version()
            if wt_game_version != wt_units_version:
                loguru.logger.debug(
                    f'[A] VER. MISMATCH: unit_library=v"{wt_units_version}" | game_library=v"{wt_game_version}"')
        finally:
            return wt_units_lookup

    def inspector(message=""):
        pass
        # import inspect
        # _ = inspect.stack()
        # path_full = _[1][1]
        # from_line = _[1][2]
        # from_modu = _[1][3]
        # name_file = path_full.split("ThunderTac")[-1]
        # tracker = loguru.logger.level("TRACK", no=38, color="<red>")
        # loguru.logger.log("TRACK", f"{name_file}:{from_modu}:{from_line} | {message}")

    def nxt_sort():
        if State.Client.player_obj != "":
            loguru.logger.debug(f"[P] PLAYER OBJECT: -0x{State.Client.player_obj.upper()}")
        State.Client.player_obj = ""
        State.Recorder.sortie_header = False
        State.Recorder.discover_unit = False
        State.Recorder.once_per_spawn = False

    def nxt_batt():
        loguru.logger.debug(f"[S] BATT FINISHED: {user_sesid}")
        State.Recorder.active = False
        State.Recorder.header_placed = False
        State.Messages.hangar = False
        State.Map.information = False
        acmi_zip_out()
        acmi_ftp_out()

    def handler(signal_received, frame):
        State.Recorder.active = False
        State.Recorder.header_placed = False
        State.Messages.hangar = False
        State.Map.information = False
        if os.path.exists('temp.ini'):
            os.remove('temp.ini')
        acmi_zip_out()
        # acmi_ftp_out()
        print('SIGINT or CTRL-C detected. Exiting gracefully')
        sys.exit(0)

    def area_init():
        if os.path.exists('temp.ini'):
            os.remove('temp.ini')
        tempdb = init_temp_db()
        map_info.main_def()
        location = map_info.get_info()
        tempdb.read('temp.ini')
        tempdb['MAP_INFO']['map_lookup_result'] = location
        with open('temp.ini', 'w') as f:
            tempdb.write(f)
        map_total_x, map_total_y = map_info.get_data()
        lat = map_total_x / 111302
        long = map_total_y / 111320
        return lat, long, location, tempdb

    def acmi_zip_out():
        if os.path.isfile(filename):
            try:
                import zlib
                compression = zipfile.ZIP_DEFLATED
            except (ImportError, AttributeError):
                compression = zipfile.ZIP_STORED
            modes = {
                zipfile.ZIP_DEFLATED: 'deflated',
                zipfile.ZIP_STORED: 'stored',
            }
            with zipfile.ZipFile(f'{filename}.zip', mode='w') as f:
                mode_name = modes[compression]
                loguru.logger.debug(f'Adding "{filename}" to "{filename}.zip" using mode "{mode_name}"')
                f.write(f'{filename}', compress_type=compression)

    def acmi_ftp_out():
        plfile = pathlib.Path(filename)
        if plfile.is_file():
            filename_parts = plfile.parts
            if ftp_send:
                ftp = ftplib.FTP(ftp_addr, ftp_user, ftp_pass)
                try:
                    file = open(f'{filename}.zip', 'rb')
                except FileNotFoundError:
                    print('file not found')
                except UnboundLocalError:
                    print('unknown exception')


                try:
                     ftp.cwd(filename_parts[0])
                except ftplib.error_perm as e:
                    ftp.mkd(filename_parts[0])
                    ftp.cwd(filename_parts[0])
                finally:
                    try:
                         ftp.cwd(filename_parts[1])
                    except ftplib.error_perm as e:
                        ftp.mkd(filename_parts[1])
                        ftp.cwd(filename_parts[1])
                ftp.storbinary(f'STOR {plfile.name}.zip', file)
                file.close()
                ftp.quit()

            # # DEPRECIATED
            # if ftp_send:
            #     session = FTP(ftp_addr, ftp_user, ftp_pass)
            #     file = open(filename + '.zip', 'rb')  # file to send
            #     session.storbinary('STOR {}'.format(filename + '.zip'), file)  # send the file
            #     file.close()  # close file and FTP
            #     session.quit()

            # # MEGA
            # mega = Mega()
            # m = mega.login("warthundertacview@gmail.com", "warthundertacview")
            # folder = m.find(f'{user_sesid}')
            # try:
            #     print('try')
            #     folder[0]
            # except:
            #     print('except')
            #     m.create_folder(f'{user_sesid}')
            # else:
            #     print('else')
            #     m.create_folder(f'{user_sesid}')
            #     folder = m.find(f'{user_sesid}')
            # finally:
            #     print('finally')
            #     m.upload(f'{filename}.zip', folder[0])

    class State:
        class Client:
            player_obj = ""
            parachute = ""

        class FileWrite:
            discover_unit = False

        class GameState:
            if platform.system() == "Windows":
                TITLE_HANG = "War Thunder"
                TITLE_LOAD = "War Thunder - Loading"
                TITLE_BATT = "War Thunder - In battle"
                TITLE_DRIV = "War Thunder - Test Drive"
                TITLE_TEST = "War Thunder - Test Flight"
                TITLE_WAIT = "War Thunder - Waiting for game"
                TITLE_DX32 = "War Thunder (DirectX 11, 32bit) - In battle"
            elif platform.system() == "Linux":
                TITLE_HANG = "War Thunder (Vulkan, 64bit)"
                TITLE_LOAD = "War Thunder (Vulkan, 64bit) - Loading"
                TITLE_BATT = "War Thunder (Vulkan, 64bit) - In battle"
                TITLE_DRIV = "War Thunder (Vulkan, 64bit) - Test Drive"
                TITLE_TEST = "War Thunder (Vulkan, 64bit) - Test Flight"
                TITLE_WAIT = "War Thunder (Vulkan, 64bit) - Waiting for game"
            # PLACEHOLDER = "War Thunder OpenGL"
            # PLACEHOLDER = "War Thunder D3DX9"

        class Map:
            information = False

        class Messages:
            rec_end = True
            hangar = False
            trigger_chat = False

        class Recorder:
            active = False
            header_placed = False
            discover_unit = False
            sortie_header = False
            gamechat_start = True
            once_per_spawn = False

    class WebAPI:
        BASE = f"http://{net_host}:{net_port}"
        LMAP = f"{BASE}/map.img"
        INFO = f"{BASE}/map_info.json"
        STAT = f"{BASE}/state"
        INDI = f"{BASE}/indicators"
        OBJT = f"{BASE}/map_obj.json"
        CHAT = f"{BASE}/gamechat"
        HMSG = f"{BASE}/hudmsg"
    last_id_msg = 0
    last_id_evt = 0
    last_id_dmg = 0

    unit_lookup = get_unit()
    ntp = ntplib.NTPClient()
    tick0 = time.perf_counter()

    # players_uid = cfg.players_uid
    # players_cid = cfg.players_cid

    id_kill_list = []
    print_once = {'in_lobby': False,
                  'in_match': False,
                  'in_fight': False}

    pp = pprint.PrettyPrinter(width=100, compact=False)
    _dict_sesid = collections.OrderedDict()
    _list_teams = []
    time_start = time.time()

    if ttac_usr is None or ttac_usr == '':
        config1.get_user_alias()
    # platform_data = {
    #     'Darwin': {
    #         'name': 'aces',
    #         'path': 'My Games/WarThunder'
    #     },
    #     'Linux': {
    #         'name': 'aces',
    #         'path': '.config/WarThunder'
    #     },
    #     'Windows': {
    #         'name': 'aces.exe',
    #         'path': 'Documents/My Games/WarThunder'
    #     }
    # }
    #
    # user_ops_system_ = platform.system()

    # have_proc_id_list = False
    # aces_chk_running = False
    #
    # while not aces_chk_running:
    #     aces_chk_running = check_for_aces(platform_data[user_ops_system_]['name'])
    #
    # while not have_proc_id_list:
    #     procObjList = [p for p in psutil.process_iter() if platform_data[user_ops_system_]['name'] in p.name()]
    #     try:
    #         path_war_rootdir = pathlib.Path(procObjList[0].exe()).parent.parent
    #     except IndexError:
    #         pass
    #     else:
    #         have_proc_id_list = True

    # path_usr_rootdir = pathlib.Path.home()

    # listOfProcessIds = findProcIdByName(platform_data[platform.system()]['name'])
    # procObjList = [p for p in psutil.process_iter() if 'aces.exe' in p.name()]
    # path_usr_rootdir = pathlib.Path.home()

    # path_cfg_endings = platform_data[platform.system()]['path']
    # path_cfg_rootdir = path_usr_rootdir.joinpath(path_cfg_endings)
    # path_cfg_file_is = path_cfg_rootdir.joinpath('thundertac.ini')

    # path_war_gamever = path_war_rootdir.joinpath('content/pkg_main.ver')
    # path_war_confblk = path_war_rootdir.joinpath('config.blk')
    # info_war_version = war_file_reader(path_war_gamever)
    # info_war_i18n_is = war_file_reader(path_war_confblk)

    d = {
        'Linux': pathlib.Path(cfg_root).joinpath('.game_logs/'),
        'Windows': pathlib.Path(war_path).joinpath('.game_logs/')
    }
    # path_war_clogdir = d[platform.system()]
    # temp = f"{str(path_war_clogdir)}/*.clog"
    # last_clog_fileis = max((glob.glob(temp)), key=os.path.getctime)

    # with open(last_clog_fileis, 'rb') as f:
    #     xored = f.read()
    #     xored_byte_array = bytearray(xored)
    #     unxored = unxor(xored_byte_array)
    #     text_curr = bytes(unxored).decode('ANSI')
    #     with open('unxored.txt', 'w', encoding='ANSI') as f:
    #         f.write(text_curr)
    #     #xxx = re.search(r"[\d]+\.[\d]+ \[D\].* (\w+)\[(\d+)\] successfully passed yuplay authorization",
    #     xxx = re.search(r"(\w+)\[(\d+)\] successfully passed yuplay authorization",
    #                     text_curr,
    #                     re.MULTILINE)
    #     if xxx:
    #         print(xxx.groups())
    #         ttac_usr, user_gid = xxx.group(1), xxx.group(2)
    #


    def mqtt_con(client, userdata, flags, rc):
        loguru.logger.debug(f"[Q] CONNECTED: Connected with result code {str(rc)}")

    def on_message(client, userdata, msg):
        # global user_sesid
        # global time_isset
        print("{}| {}".format(msg.topic, msg.payload.decode()))
        # print(str(msg.payload.decode("utf-8")), msg.topic, msg.retain)
        # try:
        #     if msg.topic.split('TTAC/')[1].split('/TIME_START')[0] == user_sesid:
        #         time_isset = True
        #         input('caught')
        #
        #     # returnmsg = msg.topic
        #     # left = returnmsg.split('TTAC/')[1]
        #     # right = left.split('/TIME_START')[0]
        #     # print(time_isset)
        #     # print(dir(client), '\n', dir(userdata), '\n', dir(client), '\n')
        #     print("{}| {}".format(msg.topic, msg.payload.decode()))
        #     # print("message received  ", str(msg.payload.decode("utf-8")), "topic", msg.topic, "retained ", msg.retain)
        #     # if msg.retain == 1:
        #     #     print("This is a retained message")
        # except NameError as e:
        #     print(e)

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print(mid)

    client = mqtt.Client()
    client.on_connect = mqtt_con
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    # 0
    while True:

        # SIGINT: INIT
        signal(SIGINT, handler)

        # DISCOVER: WINDOW TITLE
        curr_game_state = window_title()

        # PROGRAM STATE: IN HANGAR
        if curr_game_state == State.GameState.TITLE_HANG:

            # STDOUT: RETURNED TO HANGAR
            if not State.Messages.hangar:
                loguru.logger.info("[S] IDLE @ HANGAR: JOIN (TEST|BATTLE|CUSTOM)")
                State.Messages.hangar = True

            # # STDOUT: RECORDING FINISHED
            # if not State.Messages.rec_end:
            #     loguru.logger.info("[R] THUNDERTAC RECORDING HAS TERMINATED")
            #     State.Messages.rec_end = True

        # PROGRAM STATE: TEST FLIGHT
            """elif curr_game_state == State.GameState.TITLE_TEST:

            # CHECK: LOCATION DATA
            if not State.Map.information:

                lati_m, long_m, map_area, temp_db = area_init()
                if lati_m is not None and long_m is not None:
                    State.Map.information = True
            State.Recorder.sortie_header = False
            State.Recorder.active = True
            time_rec_start = time.time()"""

        # PROGRAM STATE: IN BATTLE
        elif curr_game_state == State.GameState.TITLE_BATT:

            # CHECK: LOCATION DATA
            if not State.Map.information:
                lati_m, long_m, map_area, temp_db = area_init()
                if lati_m is not None and long_m is not None:

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
                        except LookupError:
                            print('IF THIS IS THE FIRST TIME RUNNING THUNDERTAC, '
                                  'PLEASE JOIN & LEAVE A CUSTOM BATTLE, THEN RESTART')
                            sys.exit()

                    split_lines = text_curr.split('\n')
                    user_sesid = get_user_sesid(split_lines, _dict_sesid)[-1]
                    users_team = get_users_team(split_lines, _list_teams, ttac_usr)[-1]
                    team_color = None

                    client.connect("tacserv.tk", 1883, 60, )
                    client.loop_start()

                    # client.subscribe(f"TTAC/{user_sesid}/TIME_START")
                    client.publish(f'TTAC/{user_sesid}/players/{user_gid}',
                                   f"{ttac_usr} is fighting for team {users_team}.", retain=True)
                State.Map.information = True

            # if not State.Messages.trigger_chat:
            #     loguru.logger.debug(f"[T] START TRIGGER: MASTER={ttac_mas}, TRIGGER={ttac_rec}")
            #     loguru.logger.info(f"[R] START TRIGGER: Waiting for {ttac_mas} ")
            #     State.Messages.trigger_chat = True

            if State.Recorder.gamechat_start:
                if State.Map.information:  # and State.Messages.trigger_chat is False:
                    if debug_on:
                        loguru.logger.debug("[D] DEBUG TRIGGER: RECOGNIZED")
                        time_rec_start = time.time()
                        loguru.logger.info("[R] RECORDING STARTED")
                        loguru.logger.debug("[R] TIME:" + str(time_rec_start))
                        State.Recorder.sortie_header = False
                        State.Recorder.active = True
                        if not time_isset:
                            client.publish(f'TTAC/{user_sesid}/times/{user_gid}',
                                           f"{time_rec_start}", retain=True)
                            time_isset = True

                    # try:
                    #     gamechat_req = gamechat()
                    #     list_msglog = gamechat_req
                    #     if list_msglog:
                    #         last_msg = list_msglog[-1]["msg"]
                    #         last_mode = list_msglog[-1]["mode"]
                    #         last_sender = list_msglog[-1]["sender"]
                    #         if last_msg == ttac_rec:
                    #             if last_sender == ttac_mas:
                    #                 State.Messages.trigger_chat = True
                    #                 loguru.logger.debug(f"[T] START TRIGGER: {ttac_mas} has started the recording")
                    #                 time_rec_start = time.time()
                    #                 loguru.logger.info("[R] START TRIGGER: Recording telemetry..")
                    #                 loguru.logger.debug(f"[R] RECORDER INIT: TIME: {str(time_rec_start)}")
                    #                 State.Recorder.sortie_header = False
                    #                 State.Recorder.active = True
                    #                 if ttac_usr == ttac_mas:
                    #                     client.publish(f'TTAC/{user_sesid}/TIME_START', f"{time_rec_start}", retain=True)
                    #
                    # except requests.exceptions.ReadTimeout as e:
                    #     pass

        while State.Recorder.active:
            try:
                hudMsg_dmg_return = hudmsg(0, last_id_dmg)['damage']
                if hudMsg_dmg_return:
                    # for messages in hudMsg_dmg_return:
                    #     print(messages['id'], messages['msg'])
                    last_list = hudMsg_dmg_return
                    last_id_dmg = last_list[-1]['id']
            except TypeError:
                pass
            # hudmsgs = get_web_reqs('http://localhost:8111/hudmsg?lastEvt=0&lastDmg=0')
            # this_id = hudmsgs['damage'][-1]['id']
            # this_msg = hudmsgs['damage'][-1]['msg']
            # damage_dict = this_msg.split(' ')
            # print(damage_dict)
            # alias = ttac_usr'
            # testcase = (alias and ('crashed.' or ('shot' and 'down')))
            #
            # if testcase in damage_dict:  # and this_id not in id_kill_list:
            #     id_kill_list.append(this_id)
            #     in_fight = False
            #     print_once['in_fight'] = False
            #     sys.exit()

            if window_title() == State.GameState.TITLE_HANG:
                nxt_sort()
                nxt_batt()
                break


            try:
                map_objects = get_web_reqs(WebAPI.OBJT)
            except json.decoder.JSONDecodeError as e:
                loguru.logger.exception(str(e))
                State.Recorder.active = False
                break


            if map_objects and not State.Recorder.header_placed:
                filename = set_filename()
                insert_header(map_area, get_utc_offset(), ttac_usr, user_sesid)
                State.Recorder.header_placed = True
            time_this_tick = time.time()
            time_adjusted_tick = arrow.get(time_this_tick - time_rec_start).float_timestamp

            try:
                player = [el for el in map_objects if el["icon"] == "Player"][0]
            except TypeError as e:
                inspector(e)

            except (IndexError, TypeError) as err:
                try:
                    # if this succeeds, continue will execute
                    player = [el for el in map_objects if el["icon"] == "Player"][0]
                # exception catches loss of player object on map_obj.json
                except (IndexError, TypeError):
                    pass
                    # TODO: test placing player_fetch_fail here
                else:
                    # this causes current iteration of loop to stop
                    continue

                # if this gets set to true, couldn't retrieve player map_obj info
                player_fetch_fail = True

                # if object id assigned, player info get failed, and alt is known
                if State.Client.player_obj and player_fetch_fail and z is not None:
                    # case: player already had object assigned and map_obj.json (player) update failed

                    with open(filename, "a", encoding="utf8", newline="") as g:
                        g.write("#{}".format(time_adjusted_tick) + "\n")
                        g.write("-" + State.Client.player_obj + "\n")
                        g.write("0,Event=Destroyed|" + State.Client.player_obj + "|" + "\n")
                        # if z > 15 and ias > 100:
                        #     State.Client.parachute = set_user_object()
                        #     parachute_align_gravity = time_adjusted_tick + 3
                        #     parachute_touchdown_time = (parachute_down(z) + parachute_align_gravity)
                        #     g.write(
                        #         "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                        #         "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                        #             time_adjusted_tick, State.Client.parachute, x, y, z, r, p, h, z
                        #         )
                        #     )
                        #     g.write(
                        #         "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                        #         "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                        #             parachute_align_gravity, State.Client.parachute, x, y, z - 15, 0, 0, h, z - 15,
                        #         )
                        #     )
                        #     g.write(
                        #         "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                        #         "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                        #             parachute_touchdown_time, State.Client.parachute, x, y, 0, 0, 0, h, 0,
                        #         )
                        #     )
                        #     g.write(
                        #         "#{:0.2f}\n-{}\n0,Event=Destroyed|{}|\n".format(
                        #             parachute_touchdown_time,
                        #             State.Client.parachute,
                        #             State.Client.parachute,
                        #         )
                        #     )
                        nxt_sort()
                        inspector()
                        curr_game_state = window_title()

                        if curr_game_state == State.GameState.TITLE_HANG:
                            loguru.logger.info("[S] UNKNOWN")
                            State.Recorder.active = False
                            State.Map.information = False
                            # TODO: INCO INTO RESET()
                            # acmi_zip_out()
                            # acmi_ftp_out()
                            State.Recorder.discover_unit = False

                        continue

                elif not State.Client.player_obj and player_fetch_fail:
                    continue

            else:
                # player map_obj.json was successful so player is still alive
                player_fetch_fail = False

            # if object_id not assigned, and map_obj was successful
            if not State.Client.player_obj and not player_fetch_fail:
                State.Client.player_obj = set_user_object()
                loguru.logger.debug(f"[P] PLAYER OBJECT: +0x{State.Client.player_obj.upper()}")

            try:
                x = player["x"] * lati_m
                y = player["y"] * long_m * -1
            except NameError as e:
                inspector(e)
            except TypeError as e:
                inspector(e)

            try:
                ind = get_web_reqs(WebAPI.INDI)
                sta = get_web_reqs(WebAPI.STAT)
                # for key, value in sta.items():
                #     if key != ('valid' or 'type'):
                #         sta[key] = float(value)

                if sta["valid"] and ind["valid"]:
                    z = sta["H, m"]
                    ias = sta["IAS, km/h"] * CONVTO_MPS
                    tas = sta["TAS, km/h"] * CONVTO_MPS
                    fuel_kg = sta["Mfuel, kg"]
                    fuel_vol = f = sta["Mfuel, kg"] / sta["Mfuel0, kg"]
                    m = sta["M"]
                    try:
                        aoa = sta["AoA, deg"]
                    except KeyError:
                        aoa = None
                    s_throttle1 = sta["throttle 1, %"] / 100
                    try:
                        flaps = sta["flaps, %"] / 100
                    except KeyError:
                        flaps = None
                    try:
                        gear = sta["gear, %"] / 100
                    except KeyError:
                        gear = 1

                try:
                    # if ind is not None and ind["valid"] and temp_test == "playing":
                    temp_test = gaijin_state_method()
                    if ind["valid"] and temp_test == "playing":
                        try:
                            ind = get_web_reqs(WebAPI.INDI)
                            try:
                                if temp_test == "playing":
                                    r = ind["aviahorizon_roll"] * -1
                                    p = ind["aviahorizon_pitch"] * -1
                            except KeyError as err_plane_not_compatible:
                                if gaijin_state_method() == "playing":
                                    # TODO: Include this in the play_once controller
                                    loguru.logger.error("[P] This plane is not supported")
                            if not State.Recorder.discover_unit:
                                unit = ind["type"]
                                try:
                                    loguru.logger.info(
                                        f"[P] UNIT RE-SPAWN: {unit_lookup['units'][unit]['full']}")
                                except KeyError:
                                    loguru.logger.error("[D] ENTRY MISSING: {}".format(unit))
                                    loguru.logger.info("[P] UNIT RE-SPAWN: {}".format(unit))
                                State.Recorder.discover_unit = True
                                # try:
                                #     fname, lname, sname = unit_lookup['units'][ind["type"]].values()
                                # except KeyError:
                                #     loguru.logger.error("[D] ENTRY MISSING: {}".format(ind["type"]))
                                #     fname = lname = sname = ind["type"]
                                # finally:
                                #     loguru.logger.info("[P] UNIT RE-SPAWN: {}".format(lname))
                                # State.Recorder.discover_unit = True
                        except Exception as err:
                            inspector(err)
                        try:
                            pedals = ind["pedals"]
                        except KeyError:
                            try:
                                pedals = ind["pedals1"]
                            except KeyError:
                                pedals = None

                        try:
                            stick_ailerons = ind["stick_ailerons"]
                        except KeyError:
                            stick_ailerons = None
                        try:
                            stick_ailerons = ind["stick_ailerons"]
                        except KeyError:
                            stick_elevator = None

                        try:
                            h = ind["compass"]
                        except KeyError:
                            h = hdg(player["dx"], player["dy"])

                        if not State.Recorder.once_per_spawn:
                            fname, lname, sname = unit_lookup['units'][unit].values()
                            State.Recorder.once_per_spawn = True

                        if users_team == "1":
                            team_color = "Blue"
                        elif users_team == "2":
                            team_color = "Red"
                        else:
                            team_color = None

                        # APPEND TO .ACMI EVERY FRAME/TICK
                        sortie_telemetry = (
                                f"#{time_adjusted_tick:0.2f}\n"
                                + f"{State.Client.player_obj},T={x:0.9f}|{y:0.9f}|{z}|{r:0.1f}|{p:0.1f}|{h:0.1f},"
                                + f"Throttle={s_throttle1},"
                                + f"RollControlInput={stick_ailerons},"
                                + f"PitchControlInput={stick_elevator},"
                                + f"YawControlInput={pedals},"
                                + f"IAS={ias:0.6f},"
                                + f"TAS={tas:0.6f},"
                                + f"FuelWeight={fuel_kg},"
                                + f"Mach={m},"
                                + f"AOA={aoa},"
                                + f"FuelVolume={fuel_vol},"
                                + f"LandingGear={gear},"
                                + f"Flaps={flaps},"
                            # + "PilotHeadRoll={},".format(PilotHeadRoll)
                            # + "PilotHeadPitch={},".format(PilotHeadPitch)
                            # + "PilotHeadYaw={},".format(PilotHeadYaw)
                        )
                        # APPEND TO .ACMI ONLY ONCE PER SPAWN
                        sortie_subheader = (
                                "Slot={'0'},"
                                + f"Importance={'1'},"
                                + f"Parachute={'0'},"
                                + f"DragChute={'0'},"
                                + f"Disabled={'0'},"
                                + f"Pilot={ttac_usr},"
                                + f"Name={sname},"
                                + f"ShortName={sname},"
                                + f"LongName={lname},"
                                + f"FullName={fname},"
                                + f"Type={'Air+FixedWing'},"
                                + f"Color={team_color},"
                                + f"Callsign={'None'},"
                                + f"Coalition={'None'},"
                        )

                        with open(filename, "a", encoding="utf8", newline="") as g:
                            if not State.Recorder.sortie_header:
                                g.write(sortie_telemetry + sortie_subheader + "\n")
                                State.Recorder.sortie_header = True
                            else:
                                g.write(sortie_telemetry + "\n")
                except KeyError as err:
                    pass  # inspector(err)
                except TypeError as err:
                    if State.Recorder.active:
                        pass

            except json.decoder.JSONDecodeError as e:
                loguru.logger.exception(str(e))
            except (TypeError, NameError) as e:
                loguru.logger.exception(str(e))
            # except KeyError as e:
            #     loguru.logger.exception(str(e))


if __name__ == "__main__":
    main_fun()
