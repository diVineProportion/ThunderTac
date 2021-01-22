user_sesid = ''
map_area = None
mission_category = None


# import snoop
# @snoop

def main_fun():
    global user_sesid
    global map_area
    global mission_category

    # built in imports
    import collections
    import configparser
    import ftplib
    import glob
    import math
    import os
    import pathlib
    import random
    import re
    import sys
    import time
    import zipfile

    from signal import signal, SIGINT

    # 3rd party imports
    import arrow
    import loguru
    import ntplib
    import paho.mqtt.client as mqtt
    import platform
    import requests
    import simplejson
    import simplejson as json

    # loguru.logger.add("file_{time}.log")

    # fmt = "{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"
    # loguru.logger.add(sys.stdout, format=fmt)

    # from mega import Mega
    # from requests.exceptions import RequestException

    import map_info
    import config

    configuration = config.CFG()

    net_host = configuration.cfg_net['net_host']
    net_port = configuration.cfg_net['net_port']
    ttac_usr = configuration.cfg_gen['ttac_usr']
    # ttac_mas = configuration.cfg_gen['ttac_mas']
    # ttac_rec = configuration.cfg_gen['ttac_rec']
    # ttac_int = configuration.cfg_gen['ttac_int']
    user_gid = configuration.cfg_gen['user_gid']
    # war_lang = configuration.cfg_gen['war_lang']
    war_lang = configuration.i18n[:-1].replace('"', '')
    # logger_l = configuration.cfg_log['logger_l']
    # debug_on = configuration.cfg_dbg['debug_on']
    ftp_send = configuration.cfg_ftp['ftp_send']
    ftp_addr = configuration.cfg_ftp['ftp_addr']
    ftp_user = configuration.cfg_ftp['ftp_user']
    ftp_pass = configuration.cfg_ftp['ftp_pass']
    # init_run = configuration.cfg_cfg['init_run']
    war_path = configuration.cfg_dir['war_path']
    cfg_root = configuration.cfg_dir['cfg_root']

    cp = configparser.ConfigParser()
    cp.read(configuration.tacx_settings_file)
    # init_run = cp['configinit'].getboolean('init_run')
    # debug_on = cp['debug'].getboolean('debug_on')

    # loguru.logger.remove()
    # loguru.logger.add(sys.stderr, level=logger_l)

    # TODO: CLEAN THIS GARBAGE UP
    filename = ""
    users_team = "0"
    time_rec_start = None
    # rec_start_mode_gamechat = True
    # map_objects = None
    # TODO: write function to automatically handle this;
    #  start false, set true individually, then reset at appropriate time.
    player_fetch_fail = None
    x = y = z = r = p = None
    ias = player = latitude = longitude = None
    unit = s_throttle1 = tas = fuel_kg = None
    m = aoa = fuel_vol = gear = flaps = None
    # stick_ailerons = stick_elevator = None
    # ind = sta = None

    # yet_done_ships = False
    # ships_dict = {}

    # __import__('ipdb').set_trace(context=9)
    # ipdb.set_trace(context=21)

    re_get_sesid = re.compile(r'[\d]+\.[\d]+ \[D] {2}'
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
    xor_key = bytearray(b"\x82\x87\x97\x40\x8D\x8B\x46\x0B\xBB\x73\x94\x03\xE5\xB3\x83\x53"
                        b"\x69\x6B\x83\xDA\x95\xAF\x4A\x23\x87\xE5\x97\xAC\x24\x58\xAF\x36"
                        b"\x4E\xE1\x5A\xF9\xF1\x01\x4B\xB1\xAD\xB6\x4C\x4C\xFA\x74\x28\x69"
                        b"\xC2\x8B\x11\x17\xD5\xB6\x47\xCE\xB3\xB7\xCD\x55\xFE\xF9\xC1\x24"
                        b"\xFF\xAE\x90\x2E\x49\x6C\x4E\x09\x92\x81\x4E\x67\xBC\x6B\x9C\xDE"
                        b"\xB1\x0F\x68\xBA\x8B\x80\x44\x05\x87\x5E\xF3\x4E\xFE\x09\x97\x32"
                        b"\xC0\xAD\x9F\xE9\xBB\xFD\x4D\x06\x91\x50\x89\x6E\xE0\xE8\xEE\x99"
                        b"\x53\x00\x3C\xA6\xB8\x22\x41\x32\xB1\xBD\xF5\x28\x50\xE0\x72\xAE")

    def un_xor(data):
        d_data = bytearray(len(data))
        key_length = len(xor_key)
        for i, c in enumerate(data):
            d_data[i] = c ^ xor_key[(i % key_length)]
        return d_data

    def get_user_session_id(text, _dict):
        list_of_team_ids = []
        list_of_session_ids = []
        for idx_line, text_line in enumerate(text):
            regex_result = re_get_sesid.search(text_line) or None
            if regex_result:
                try:
                    time_elapsed = time.time() - time_start
                    session_id = regex_result.group(1)
                    list_of_session_ids.append(session_id)
                    list_of_team_ids.append(time_elapsed)
                    _dict[max(list_of_team_ids)] = {'session_id': list_of_session_ids[-1]}
                except AttributeError:
                    pass
        return list_of_session_ids

    def get_users_team(text, _list_teams, alias):
        for idx_line, text_line in enumerate(text):
            x2 = re_get_teams.search(text_line) or None
            if x2 is not None:
                if x2.group(2) == alias:
                    _list_teams.append(x2.group(5))
        return _list_teams

    def gaijin_state_method():
        """last_state.blk is created and updated live but hasn't been implemented in thundertac"""
        while True:
            _ = platform.system()
            try:
                path_user_cfg = None
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
        sdate, stime = (str(arrow.utcnow())[:-13]).replace(":", ".").split("T")
        # ldate, ltime = (str(arrow.now())[:-13]).replace(":", ".").split("T")
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
        except simplejson.errors.JSONDecodeError:
            pass

    def get_window_title():
        lang_dict = {
            "English": {
                "load": "Loading",
                "batt": "In battle",
                "driv": "Test Drive",
                "test": "Test Flight",
                "wait": "Waiting for game"
            },
            "French": {
                "load": "Téléchargement en cours",
                "batt": "Dans la bataille",
                "driv": "Test Drive",
                "test": "Vol test",
                "wait": "En attente du jeu"
            }
        }

        if configuration.players_sys == "Darwin":
            pass
        elif configuration.players_sys == "Linux":
            render_engine = "(Vulkan, 64bit)"
        elif configuration.players_sys == "Windows":
            render_engine = ''

        base = 'War Thunder'

        if render_engine != '':
            base = f'{base} {render_engine}'

        title_hang = f'{base}'
        title_load = f'{base} - {lang_dict[war_lang]["load"]}'
        title_batt = f'{base} - {lang_dict[war_lang]["batt"]}'
        title_driv = f'{base} - {lang_dict[war_lang]["driv"]}'
        title_test = f'{base} - {lang_dict[war_lang]["test"]}'
        title_wait = f'{base} - {lang_dict[war_lang]["wait"]}'

        if platform.system() == "Linux":
            import ewmh
            window_manager = ewmh.EWMH()
            title_hang = bytes(title_hang, 'utf-8')
            title_load = bytes(title_load, 'utf-8')
            title_batt = bytes(title_batt, 'utf-8')
            title_driv = bytes(title_driv, 'utf-8')
            title_test = bytes(title_test, 'utf-8')
            title_wait = bytes(title_wait, 'utf-8')
            list_window_titles = [title_hang, title_wait, title_batt, title_load, title_driv, title_test]
            try:
                client_list = window_manager.getClientList()
                for window in client_list:
                    if window_manager.getWmName(window) in list_window_titles:
                        window_title_from_window_id = window_manager.getWmName(window)
                        return window_title_from_window_id
            except Exception as err_ewmh:
                print(err_ewmh)

                #     title_hang = b'War Thunder (Vulkan, 64bit)'
                #     title_load = b'War Thunder (Vulkan, 64bit) - Loading'
                #     title_batt = b'War Thunder (Vulkan, 64bit) - In battle'
                #     title_driv = b'War Thunder (Vulkan, 64bit) - Test Drive'
                #     title_test = b'War Thunder (Vulkan, 64bit) - Test Flight'
                #     title_wait = b'War Thunder (Vulkan, 64bit) - Waiting for game'
                # elif war_lang == "French":
                #     title_hang = b'War Thunder (Vulkan, 64bit)'
                #     title_load = b'War Thunder (Vulkan, 64bit) - T\xc3\xa9l\xc3\xa9chargement en cours'
                #     title_batt = b'War Thunder (Vulkan, 64bit) - Dans la bataille'
                #     title_driv = b'War Thunder (Vulkan, 64bit) - Essai du v\xc3\xa9hicule'
                #     title_test = b'War Thunder (Vulkan, 64bit) - Vol test'
                #     title_wait = b'War Thunder (Vulkan, 64bit) - En attente du jeu'

                # title_hang = bytes("War Thunder (Vulkan, 64bit)", "utf-8")
                # title_load = bytes("War Thunder (Vulkan, 64bit) - Téléchargement en cours", "utf-8")
                # title_batt = bytes("War Thunder (Vulkan, 64bit) - Dans la bataille", "utf-8")
                # title_driv = bytes("War Thunder (Vulkan, 64bit) - Test Drive", "utf-8")
                # title_test = bytes("War Thunder (Vulkan, 64bit) - Vol test", "utf-8")
                # title_wait = bytes("War Thunder (Vulkan, 64bit) - En attente du jeu", "utf-8")
                # b'War Thunder (Vulkan, 64bit)'
                # b'War Thunder (Vulkan, 64bit) - Vol test'(Test Flight)
                # b'War Thunder (Vulkan, 64bit) - T\xc3\xa9l\xc3\xa9chargement en cours'(Loading)
                # b'War Thunder (Vulkan, 64bit) - Essai du v\xc3\xa9hicule'(Test Drive)
                # b'War Thunder (Vulkan, 64bit) - Dans la bataille'(In Battle)

        elif platform.system() == "Windows":
            from win32gui import FindWindowEx
            list_window_titles = [title_hang, title_wait, title_batt, title_load, title_driv, title_test]
            for window_title in list_window_titles:
                window_handle = FindWindowEx(None, None, None, window_title)
                if not (window_handle == 0):
                    return window_title

    def hdg(dx, dy):
        """Fallback in case compass is missing from indicators panel"""
        dx *= longitude
        dy *= latitude
        return int(180 - (180 / math.pi) * math.atan2(dx, dy))

    def insert_header(region, ref_time, alias, session_id='', category='', ttac_ver='0.0.0'):

        comment_string = f"War Thunder v{str(configuration.get_game_version())}\\, " \
                         f"Thunder Tac v{ttac_ver}\\, " \
                         f"Session ID: {session_id}" \
                         f"\n"

        # run_date, run_time = (str(arrow.now())[:-13]).replace(":", ".").split("T")

        acmi_header = (
            f"FileType={'text/acmi/tacview'}\n"
            f"FileVersion={'2.1'}\n"
            f"0,DataSource=War Thunder\n"
            f"0,DataRecorder=Thunder Tac\n"
            f"0,ReferenceTime={ref_time}Z\n"
            f"0,RecordingTime={(str(arrow.now())[:-13])}Z\n"
            f"0,Author={alias}\n"
            f"0,Title={(get_window_title()[14:]).title()}: {region}\n"
            f"0,Category={category}\n"
            f"0,Briefing={'None Provided'}\n"
            f"0,Debriefing={'None Provided'}\n"
            f"0,Comments={comment_string}"
            f"0,ReferenceLongitude={'0'}\n"
            f"0,ReferenceLatitude={'0'}\n"
        )

        with open(filename, "a", newline="") as f_a_acmi_header:
            f_a_acmi_header.write(acmi_header)

    def set_user_object():
        """Object ID assigner"""
        max_object_id = 0xFFFFFFFFFFFFFFFF
        random_object_id = random.randint(0, int(max_object_id))
        return hex(random_object_id)[2:]

    # def get_game_chat(id_msg=0):
    #     url_game_chat = f"{WebAPI.CHAT}?lastId={id_msg}"
    #     url_game_chat = url_game_chat.format(id_msg)
    #     req_game_chat = requests.get(url_game_chat, timeout=0.02)
    #     return req_game_chat.json()
    #
    # def get_hud_msg(last_event=0, last_damage=0):
    #     try:
    #         hud_msg_request = f"{WebAPI.HMSG}?lastEvt={last_event}&lastDmg={last_damage}"
    #         hud_msg_response = requests.get(hud_msg_request, timeout=0.02).json()
    #         return hud_msg_response
    #     except (IndexError, requests.exceptions.ReadTimeout) as err_get_hud_msg:
    #         loguru.logger.debug(err_get_hud_msg)

    def get_unit():
        wt_units_lookup = None
        try:
            with open('resources/wtunits.json', 'r', encoding='utf-8') as fo:
                wt_units_lookup = json.loads(fo.read())
        except FileNotFoundError:
            wt_units_host = 'https://raw.githubusercontent.com/diVineProportion/ThunderTac/ThunderTacX/wtunits.json'
            wt_units_data = requests.get(wt_units_host).json()
            wt_units_version = wt_units_data['version']
            loguru.logger.info(f"[A] UNITS LIBRARY: War Thunder v'{wt_units_version}' Loaded")
            wt_game_version = configuration.get_game_version()
            if wt_game_version != wt_units_version:
                # g_major, g_minor, g_subminor, g_patch = wt_game_version.split('.')
                # v_major, v_minor, v_subminor, v_patch = wt_units_version.split('.')
                # if v_major != g_major:
                #     loguru.logger.debug(f'[A] VER. MISMATCH:
                #     if v_minor != g_minor:
                #         loguru.logger.debug(f'[A] VER. MISMATCH:
                #         if v_subminor != g_subminor:
                #             loguru.logger.debug(f'[A] VER. MISMATCH:
                #             if v_patch != g_patch:
                #                 loguru.logger.debug(f'[A] VER. MISMATCH:
                #
                loguru.logger.debug(
                    f'[A] VER. MISMATCH: unit_library=v"{wt_units_version}" | game_library=v"{wt_game_version}"')
        finally:
            return wt_units_lookup

    def nxt_sort():
        if State.Client.player_obj:
            loguru.logger.debug(f"[P] PLAYER OBJECT: -0x{State.Client.player_obj.upper()}")
        State.Client.player_obj = False
        State.Recorder.sortie_header = False
        State.Recorder.discover_unit = False
        State.Recorder.once_per_spawn = False

    def nxt_batt():
        loguru.logger.debug(f"[S] BATT FINISHED: {user_sesid}")
        State.Messages.hangar = False
        State.Map.information = False
        State.Recorder.active = False
        State.Recorder.header_placed = False
        acmi2zip()
        acmi2ftp()

    def handler(signal_received, frame):
        State.Map.information = False
        State.Recorder.active = False
        State.Messages.hangar = False
        State.Recorder.header_placed = False
        acmi2zip()
        # acmi2ftp()
        print(f'SIGINT {signal_received} from frame {frame} (or CTRL-C) detected. Exiting gracefully')
        sys.exit(0)

    def area_init():
        map_info.main_def()
        location = map_info.get_info()
        map_total_x, map_total_y = map_info.get_data()
        area_latitude = map_total_x / 111302
        area_longitude = map_total_y / 111320
        return area_latitude, area_longitude, location

    def acmi2zip():
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
            with zipfile.ZipFile(f'{filename}.zip', mode='w') as fo:
                mode_name = modes[compression]
                loguru.logger.debug(f'Adding "{filename}" to "{filename}.zip" using mode "{mode_name}"')
                fo.write(f'{filename}', compress_type=compression)

    def acmi2ftp():
        pathlib_file_object = pathlib.Path(filename)
        if pathlib_file_object.is_file():
            filename_parts = pathlib_file_object.parts
            if ftp_send:
                ftp = ftplib.FTP(ftp_addr, ftp_user, ftp_pass)
                file = None
                try:
                    file = open(f'{filename}.zip', 'rb')
                except FileNotFoundError as err_acmi_ftp_out_file_not_found:
                    loguru.logger.warning(err_acmi_ftp_out_file_not_found)
                except UnboundLocalError as err_acmi_ftp_out_unbound_local_error:
                    loguru.logger.warning(err_acmi_ftp_out_unbound_local_error)
                try:
                    ftp.cwd(filename_parts[0])
                except ftplib.error_perm as err_acmi_ftp_out_change_working_directory_1:
                    loguru.logger.debug(err_acmi_ftp_out_change_working_directory_1)
                    ftp.mkd(filename_parts[0])
                    ftp.cwd(filename_parts[0])
                finally:
                    try:
                        ftp.cwd(filename_parts[1])
                    except ftplib.error_perm as err_acmi_ftp_out_change_working_directory_2:
                        loguru.logger.debug(err_acmi_ftp_out_change_working_directory_2)
                        ftp.mkd(filename_parts[1])
                        ftp.cwd(filename_parts[1])

                ftp.storbinary(f'STOR {pathlib_file_object.name}.zip', file)
                file.close()
                ftp.quit()

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

    def parse_clog():
        if (latitude and longitude) is not None:
            path_war_clogdir = game_logs_path[platform.system()]
            temp = f"{str(path_war_clogdir)}/*.clog"
            last_clog_fileis = max((glob.glob(temp)), key=os.path.getctime)
            with open(last_clog_fileis, 'rb') as f:
                xor_ed = f.read()
                xor_ed_byte_array = bytearray(xor_ed)
                un_xor_ed = un_xor(xor_ed_byte_array)

                if configuration.players_sys == "Linux":
                    import cchardet as chardet
                    result = chardet.detect(bytes(un_xor_ed))
                    decode_type = result['encoding']
                elif configuration.players_sys == "Windows":
                    decode_type = 'ANSI'
                try:
                    result = bytes(un_xor_ed).decode(decode_type)
                except LookupError as parse_clog_lookup_error:
                    print(f'ERROR 0x1D: {parse_clog_lookup_error}')
                    sys.exit()
                else:
                    return result

    class State:
        class Client:
            player_obj = ""
            parachute = ""

        class FileWrite:
            discover_unit = False

        class GameState:
            if platform.system() == "Windows":
                print(war_lang)
                if war_lang == "English":
                    print(1)
                    TITLE_HANG = "War Thunder"
                    TITLE_LOAD = "War Thunder - Loading"
                    TITLE_BATT = "War Thunder - In battle"
                    TITLE_DRIV = "War Thunder - Test Drive"
                    TITLE_TEST = "War Thunder - Test Flight"
                    TITLE_WAIT = "War Thunder - Waiting for game"
                elif war_lang == "French":
                    print(2)
                    TITLE_HANG = "War Thunder"
                    TITLE_LOAD = "War Thunder - Téléchargement en cours"
                    TITLE_BATT = "War Thunder - Dans la bataille"
                    TITLE_DRIV = "War Thunder - Test Drive"
                    TITLE_TEST = "War Thunder - Vol test"
                    TITLE_WAIT = "War Thunder - En attente du jeu"
            elif platform.system() == "Linux":
                if war_lang == "English":
                    print(3)
                    TITLE_HANG = b"War Thunder (Vulkan, 64bit)"
                    TITLE_LOAD = b"War Thunder (Vulkan, 64bit) - Loading"
                    TITLE_BATT = b"War Thunder (Vulkan, 64bit) - In battle"
                    TITLE_DRIV = b"War Thunder (Vulkan, 64bit) - Test Drive"
                    TITLE_TEST = b"War Thunder (Vulkan, 64bit) - Test Flight"
                    TITLE_WAIT = b"War Thunder (Vulkan, 64bit) - Waiting for game"
                elif war_lang == "French":
                    print(4)
                    TITLE_HANG = "War Thunder (Vulkan, 64bit)"
                    TITLE_LOAD = "War Thunder (Vulkan, 64bit) - Téléchargement en cours"
                    TITLE_BATT = "War Thunder (Vulkan, 64bit) - Dans la bataille"
                    TITLE_DRIV = "War Thunder (Vulkan, 64bit) - Test Drive"
                    TITLE_TEST = "War Thunder (Vulkan, 64bit) - Vol test"
                    TITLE_WAIT = "War Thunder (Vulkan, 64bit) - En attente du jeu"
            else:
                TITLE_HANG = "War Thunder"
                TITLE_LOAD = "War Thunder - Loading"
                TITLE_BATT = "War Thunder - In battle"
                TITLE_DRIV = "War Thunder - Test Drive"
                TITLE_TEST = "War Thunder - Test Flight"
                TITLE_WAIT = "War Thunder - Waiting for game"

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
            start_recording = True
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

    # last_id_msg = 0
    # last_id_evt = 0
    # last_id_dmg = 0

    unit_lookup = get_unit()
    ntp = ntplib.NTPClient()

    _dict_sesid = collections.OrderedDict()
    _list_teams = []
    time_start = time.time()

    if ttac_usr is None or ttac_usr == '':
        configuration.get_user_alias()

    game_logs_path = {
        'Linux': pathlib.Path(cfg_root).joinpath('.game_logs/'),
        'Windows': pathlib.Path(war_path).joinpath('.game_logs/')
    }

    def mqtt_con(client, userdata, flags, rc):
        loguru.logger.debug(f"[Q] CONNECTED: {client} ({userdata}) connected; result code:{str(rc)}, flags:{flags}")

    def on_message(client, userdata, msg):
        print(f"{client}, {userdata} {msg.topic}| {msg.payload.decode()}")

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print(client, userdata, mid, granted_qos, properties)

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = mqtt_con
    mqtt_client.on_message = on_message
    mqtt_client.on_subscribe = on_subscribe

    state = State.GameState

    while True:

        # SIGINT: INIT
        signal(SIGINT, handler)

        # DISCOVER: WINDOW TITLE
        curr_game_state = get_window_title()

        # PROGRAM STATE: IN HANGAR
        if curr_game_state == state.TITLE_HANG:

            # STDOUT: RETURNED TO HANGAR
            if not State.Messages.hangar:
                loguru.logger.info("[S] IDLE @ HANGAR: JOIN (TEST|BATTLE|CUSTOM)")
                State.Messages.hangar = True

            # STDOUT: RECORDING FINISHED
            """if not State.Messages.rec_end:
                loguru.logger.info("[R] THUNDERTAC RECORDING HAS TERMINATED")
                State.Messages.rec_end = True"""

        # PROGRAM STATE: TEST FLIGHT
        elif curr_game_state == State.GameState.TITLE_TEST:
            mission_category = 'Test Flight'

            # CHECK: LOCATION DATA
            if not State.Map.information:
                latitude, longitude, map_area = area_init()
                if (latitude and longitude) is not None:
                    State.Map.information = True
            State.Recorder.header_placed = False
            State.Recorder.sortie_header = False
            State.Recorder.active = True
            time_rec_start = time.time()

        # PROGRAM STATE: IN BATTLE
        elif curr_game_state == State.GameState.TITLE_BATT:
            mission_category = 'Multiplayer Battle'

            # CHECK: LOCATION DATA
            if not State.Map.information:
                latitude, longitude, map_area = area_init()
                if not map_area:
                    map_area = ''
                State.Map.information = True

                decoding_result = parse_clog()

                split_lines = decoding_result.split('\n')
                user_sesid = get_user_session_id(split_lines, _dict_sesid)[-1]
                loguru.logger.debug(user_sesid)
                users_team = get_users_team(split_lines, _list_teams, ttac_usr)[-1]
                loguru.logger.debug(users_team)

                mqtt_client.connect("tacserv.tk", 1883, 60, )
                mqtt_client.loop_start()

                # client.subscribe(f"TTAC/{user_sesid}/TIME_START")
                mqtt_client.publish(f'TTAC/{user_sesid}/players/{user_gid}',
                                    f"{ttac_usr} is fighting for team {users_team}.", retain=True)

            if State.Recorder.start_recording:
                if State.Map.information:
                    time_rec_start = time.time()
                    loguru.logger.info("[R] RECORD ACTIVE:" + str(time_rec_start))
                    State.Recorder.sortie_header = False
                    State.Recorder.active = True

        # RECORDING STATE: RECORDING
        while State.Recorder.active:
            # try:
            #     hudMsg_dmg_return = get_hud_msg(0, last_id_dmg)['damage']
            #     if hudMsg_dmg_return:
            #         # for messages in hudMsg_dmg_return:
            #         #     print(messages['id'], messages['msg'])
            #         last_list = hudMsg_dmg_return
            #         last_id_dmg = last_list[-1]['id']
            # except TypeError:
            #     pass
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

            if get_window_title() == State.GameState.TITLE_HANG:
                nxt_sort()
                nxt_batt()
                break

            try:
                map_objects = get_web_reqs(WebAPI.OBJT)
            except json.decoder.JSONDecodeError as err_map_objects_json_decoder_error:
                loguru.logger.exception(str(err_map_objects_json_decoder_error))
                State.Recorder.active = False
                break

            if map_objects and not State.Recorder.header_placed:
                filename = set_filename()
                insert_header(map_area, get_utc_offset(), ttac_usr, user_sesid, mission_category, ttac_ver='')
                State.Recorder.header_placed = True

            time_this_tick = time.time()
            time_adjusted_tick = arrow.get(time_this_tick - time_rec_start).float_timestamp

            try:
                player = [el for el in map_objects if el["icon"] == "Player"][0]
            except TypeError:
                pass

            except (IndexError, TypeError):
                try:
                    player = [el for el in map_objects if el["icon"] == "Player"][0]
                    # if this succeeds, continue will execute
                except (IndexError, TypeError):
                    # exception catches loss of player object on map_obj.json
                    pass
                    # TODO: test placing player_fetch_fail here
                else:
                    continue
                    # this causes current iteration of loop to stop

                player_fetch_fail = True
                # if this gets set to true, couldn't retrieve player map_obj info

                if State.Client.player_obj and player_fetch_fail and z is not None:
                    # if object id assigned, player info get failed, and alt is known
                    # case: player already had object assigned and map_obj.json (player) update failed

                    with open(filename, "a", encoding="utf8", newline="") as g:
                        g.write(f"#{time_adjusted_tick}\n")
                        g.write(f"0,Event=Destroyed|{State.Client.player_obj}|\n")
                        g.write(f"-{State.Client.player_obj}\n")
                        nxt_sort()
                        curr_game_state = get_window_title()

                        if curr_game_state == State.GameState.TITLE_HANG:
                            State.Map.information = False
                            State.Recorder.active = False
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
                x = player["x"] * latitude
                y = player["y"] * longitude * -1
            except NameError:
                pass
            except TypeError:
                pass
            try:
                ind = get_web_reqs(WebAPI.INDI)
                sta = get_web_reqs(WebAPI.STAT)
                # for key, value in sta.items():
                #     if key != ('valid' or 'type'):
                #         sta[key] = float(value)

                if sta["valid"] and ind["valid"]:
                    z = sta["H, m"]
                    ias = sta["IAS, km/h"] * 0.277778
                    tas = sta["TAS, km/h"] * 0.277778
                    fuel_kg = sta["Mfuel, kg"]
                    fuel_vol = sta["Mfuel, kg"] / sta["Mfuel0, kg"]
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
                            except KeyError:
                                if gaijin_state_method() == "playing":
                                    # TODO: Include this in the play_once controller
                                    loguru.logger.error("[P] This plane is not supported")
                            if not State.Recorder.discover_unit:
                                unit = ind["type"]
                                if State.Client.player_obj:
                                    try:
                                        current_unit = unit_lookup['units'][unit]['full']
                                        loguru.logger.info(f"[P] UNIT RE-SPAWN: {current_unit}")
                                    except KeyError:
                                        loguru.logger.error("[D] ENTRY MISSING: {}".format(unit))
                                        loguru.logger.info("[P] UNIT RE-SPAWN: {}".format(unit))
                                    State.Recorder.discover_unit = True
                                    State.Recorder.once_per_spawn = False
                        except TypeError:
                            pass

                        def try_er(retrieve_from, alternative=None):
                            try:
                                retrieve_from
                            except KeyError:
                                alternative = alternative
                            else:
                                return retrieve_from
                            finally:
                                return alternative

                        pedals = ind['pedals1']
                        stick_ailerons = ind["stick_ailerons"]
                        stick_elevator = ind["stick_elevator"]
                        h = hdg(player["dx"], player["dy"])

                        # pedals = try_er(ind['pedals1'])
                        # stick_ailerons = try_er(ind["stick_ailerons"])
                        # stick_elevator = try_er(ind["stick_elevator"])
                        # h = try_er(hdg(player["dx"], player["dy"]))

                        fname, lname, sname = None, None, None
                        if not State.Recorder.once_per_spawn:
                            fname, lname, sname = unit_lookup['units'][unit].values()
                            State.Recorder.once_per_spawn = True

                        team_color = None
                        team_coalition = None
                        if users_team == "0":
                            team_color = "Orange"
                            team_coalition = "Neutral"
                        elif users_team == "1":
                            team_color = "Blue"
                            # team_coalition = "Star (Allies)"
                            team_coalition = "Team 1"
                        elif users_team == "2":
                            team_color = "Red"
                            # team_coalition = "Cross (Axis)"
                            team_coalition = "Team 2"
                        # TODO: doesn't work, causes wrong team
                        # else:
                        #     team_color = "Purple"
                        #     team_coalition = "Unknown"

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
                        sortie_subheader = (f"Slot={'0'}," +
                                            f"Importance={'1'}," +
                                            f"Parachute={'0'}," +
                                            f"DragChute={'0'}," +
                                            f"Disabled={'0'}," +
                                            f"Pilot={ttac_usr}," +
                                            f"Name={sname}," +
                                            f"ShortName={sname}," +
                                            f"LongName={lname}," +
                                            f"FullName={fname}," +
                                            f"Type={'Air+FixedWing'}," +
                                            f"Color={team_color}," +
                                            f"Callsign={'None'}," +
                                            f"Coalition={team_coalition}"
                                            )

                        with open(filename, "a", encoding="utf8", newline="") as g:
                            if State.Client.player_obj:
                                if not State.Recorder.sortie_header:
                                    g.write(sortie_telemetry + sortie_subheader + "\n")
                                    g.write(f"0,Event=Message|{State.Client.player_obj}|has spawned in.\n")
                                    State.Recorder.sortie_header = True
                                else:
                                    g.write(sortie_telemetry + "\n")

                except KeyError:
                    pass
                except TypeError:
                    if State.Recorder.active:
                        pass

            except json.decoder.JSONDecodeError:
                pass
            except (TypeError, NameError):
                pass
                # loguru.logger.exception(str(e))
            # except KeyError as e:
            #     loguru.logger.exception(str(e))


if __name__ == "__main__":
    from pyu_config import ClientConfig
    print(ClientConfig.APP_VERSION)
    main_fun()

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
