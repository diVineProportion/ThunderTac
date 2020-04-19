import configparser
import math
import os
import random
import sys
import time
import zipfile
from ftplib import FTP
from signal import signal, SIGINT
from sys import exit

import arrow
import loguru
import ntplib
import requests
import simplejson as json
from pyupdater.client import Client

import ttac_update
import map_info
import userinfo
from client_config import ClientConfig

windows = linux = darwin = False
platform = userinfo.system_info()
if platform == "Windows":
    windows = True
elif platform == "Linux":
    linux = True
elif platform == "Darwin":
    darwin = True


config = configparser.ConfigParser()
config.read('config.ini')
if config['configinit']['first_run'] == 'True':
    ttac_usr = input("INPUT WT ALIAS (NO SQUADRON): ")
    ttac_mas = input("INPUT TT MASTER (SAME OR ASK YOU ThunderTac HOST): ")
    config['general']['ttac_usr'] = ttac_usr
    config['general']['ttac_mas'] = ttac_mas
    config['configinit']['first_run'] = 'False'
    with open('config.ini', 'w') as f:
        config.write(f)


ttac_log = config['loguru']['level']
ttac_dbg = config['debug']['debug_on']
ttac_usr = config['general']['ttac_usr']
ttac_mas = config['general']['ttac_mas']
ttac_rec = config['general']['ttac_rec']
ftp_send = config['ftpcred']['ftp_send']
ftp_addr = config['ftpcred']['ftp_addr']
ftp_user = config['ftpcred']['ftp_user']
ftp_pass = config['ftpcred']['ftp_pass']
ftp_sess = config['ftpcred']['ftp_sess']
source_ip = config['network']['source_ip']
source_pt = config['network']['source_pt']
pyu_channel = config['pyupdater']['channel']

ftp_send = bool(ftp_send)
ttac_dbg = bool(ttac_dbg)

loguru.logger.remove()
loguru.logger.add(sys.stderr, level=ttac_log)

CONVTO_MPS = 0.277778

# TODO: CLEAN THIS GARBAGE UP
filename = ""
time_rec_start = None
rec_start_mode_gamechat = True
map_objects = None
run_once_per_spawn = False
# TODO: write function to automatically handle this; start false, set true individually, then reset at appropriate time.
player_fetch_fail = None
x = y = z = r = p = h = None
ias = player = lati_m = long_m = None
unit = s_throttle1 = tas = fuel_kg = None
m = aoa = fuel_vol = gear = flaps = None
stick_ailerons = stick_elevator = None
ind = sta = None

# __import__('ipdb').set_trace(context=9)tre


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
        try:
            if windows:
                from winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
                with open(os.environ['USERPROFILE'] + '\\Documents\\My Games\\WarThunder\\Saves\\last_state.blk',
                          'r') as fr:
                    prev_state, last_state = fr.readlines()
                # prev_state = prev_state.split('"')[1]
                last_state = last_state.split('"')[1]
                return last_state
            else:
                pass
                # TODO: linux and macos not yet implemented
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
    if not os.path.exists('.\\ACMI\\'):
        os.makedirs('.\\ACMI\\')
    sdate, stime = (str(arrow.utcnow())[:-13]).replace(":", ".").split("T")
    ldate, ltime = (str(arrow.now())[:-13]).replace(":", ".").split("T")
    temp_db.read('temp.ini')
    temp_db['HEADER_INFO']['utc_start_date'] = sdate
    temp_db['HEADER_INFO']['utc_start_time'] = stime
    temp_db['HEADER_INFO']['loc_start_date'] = ldate
    temp_db['HEADER_INFO']['loc_start_time'] = ltime
    with open('temp.ini', 'w') as f:
        temp_db.write(f)
    return f"{sdate}_{stime}_{ltime}_{players_uid}@{players_cid}"


def get_web_reqs(req_type):
    """request data from web interface"""
    wait_till_recv = False
    while not wait_till_recv:
        try:
            response = requests.get(req_type, timeout=0.1)
            if response.status_code == 200:
                return response.json()
            else:
                print(f'ERROR: {response.status_code}')
        except requests.exceptions.ReadTimeout:
            pass


def window_title():
    title_hang = "War Thunder"
    title_load = "War Thunder - Loading"
    title_batt = "War Thunder - In battle"
    title_driv = "War Thunder - Test Drive"
    title_test = "War Thunder - Test Flight"
    title_wait = "War Thunder - Waiting for game"
    title_dx32 = "War Thunder (DirectX 11, 32bit) - In battle"
    list_title = [title_hang, title_wait, title_batt, title_load, title_driv, title_test, title_dx32]

    if windows:
        import win32gui
        """Use win32api window handle titles to detect war thunder state"""
        # TODO: consider using xored clog file for more robust detection
        for window_titles in list_title:
            whnd = win32gui.FindWindowEx(None, None, None, window_titles)
            if not (whnd == 0):
                return window_titles


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


def insert_header(map_information, reference_time):
    """INSERTS MANDATORY ACMI HEADER INFORMATION"""

    acmi_header_primary = (
        "FileType={filetype}\n"
        "FileVersion={acmiver}\n"
    ).format(
        filetype="text/acmi/tacview",
        acmiver="2.1"
    )
    header_text_prop = (
        "0,DataSource=War Thunder v{datasrc}\n"
        "0,DataRecorder=Thunder Tac v{datarec}\n"
        "0,ReferenceTime={reftime}Z\n"
        "0,RecordingTime={rectime}Z\n"
        "0,Author={hdruser}@{hdrhost}\n"
        "0,Title={hdtitle}:{hdstate}\n"
        "0,Category={catgory}\n"
        "0,Briefing={briefin}\n"
        "0,Debriefing={debrief}\n"
        "0,Comments=Local: {comment}\n"
    ).format(
        datasrc=str(userinfo.get_ver_info()),
        datarec="ThunderTac",
        reftime=reference_time,
        rectime=str(arrow.utcnow())[:-13],
        hdruser=players_uid,
        hdrhost=players_cid,
        hdtitle=(window_title()[14:]).title(),
        catgory="NOT YET IMPLEMENTED",
        briefin=map_information,  # get_info().replace("_", " "),
        debrief="NOT YET IMPLEMENTED",
        hdstate=map_information,  # get_info().replace("_", " "),
        comment=arrow.now().format()[:-6],
    )

    header_numb_prop = (
        "0,ReferenceLongitude={reflong}\n"
        "0,ReferenceLatitude={reflati}\n"
    ).format(
        reflong="0",
        reflati="0"
    )

    with open(f"ACMI/{filename}.acmi", "a", newline="") as f:
        f.write(acmi_header_primary + header_text_prop + header_numb_prop)


def set_user_object():
    """Object ID assigner"""
    return hex(random.randint(0, int(0xFFFFFFFFFFFFFFFF)))[2:]


def gamechat(id_msg=0):
    url_gamechat = f"{constants.WebAPI.CHAT}?lastId={id_msg}"
    url_gamechat = url_gamechat.format(id_msg)
    req_gamechat = requests.get(url_gamechat, timeout=0.02)
    return req_gamechat.json()


def hudmsg(id_evt=0, id_dmg=0):
    url_hudmsg = f"{constants.WebAPI.HMSG}?lastEvt={id_evt}&lastDmg={id_dmg}"
    url_hudmsg = url_hudmsg.format(id_evt, id_dmg)
    req_hudmsg = requests.get(url_hudmsg, timeout=0.02)
    return req_hudmsg.json()


def get_conf():
    pass


def get_unit():
    wt_units_lookup = None
    try:
        with open('wtunits.json', 'r', encoding='utf-8') as f:
            wt_units_lookup = json.loads(f.read())
    except FileNotFoundError:
        wt_units_host = 'https://raw.githubusercontent.com/diVineProportion/ThunderTac/master/wtunits.json'
        wt_units_data = requests.get(wt_units_host).json()
        wt_units_version = wt_units_data['.ttacver']
        loguru.logger.info(f"[A] UNITS LIBRARY: War Thunder v'{wt_units_version}' Loaded")
        wt_game_version = userinfo.get_ver_info()
        if wt_game_version != wt_units_version:
            loguru.logger.warning(f"[A] UNITS LIBRARY: Game v'{wt_game_version}' does not match unit library v'{wt_units_version}'")

        wt_units_lookup = wt_units_data['units']
    finally:
        return wt_units_lookup


def inspector(message=""):
    import inspect
    _ = inspect.stack()
    path_full = _[1][1]
    from_line = _[1][2]
    from_modu = _[1][3]
    name_file = path_full.split("ThunderTac")[-1]
    tracker = loguru.logger.level("TRACK", no=38, color="<red>")
    loguru.logger.log("TRACK", f"{name_file}:{from_modu}:{from_line} | {message}")


def nxt_sort():
    loguru.logger.debug(f"[P] PLAYER OBJECT: -0x{State.Client.player_obj.upper()}")
    State.Client.player_obj = ""
    State.Recorder.sortie_header = False
    State.Recorder.discover_unit = False


def nxt_batt():
    State.Recorder.active = False
    State.Recorder.header_placed = False
    State.Messages.hangar = False
    State.Map.information = False
    acmi_zip_out()
    acmi_ftp_out()


def handler(signal_received, frame):
    if os.path.exists('temp.ini'):
        os.remove('temp.ini')
    acmi_zip_out()
    acmi_ftp_out()
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)


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
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except (ImportError, AttributeError):
        compression = zipfile.ZIP_STORED

    modes = {
        zipfile.ZIP_DEFLATED: 'deflated',
        zipfile.ZIP_STORED: 'stored',
    }

    if os.path.isfile(f"{filename}.zip"):
        with zipfile.ZipFile(f"{filename}.zip", mode='w') as f:
            mode_name = modes[compression]
            print(f"adding '{filename}.acmi' to archive using mode '{mode_name}'")
            f.write(filename + '.acmi', compress_type=compression)


def acmi_ftp_out():
    if ftp_send:
        session = FTP(ftp_addr, ftp_user, ftp_pass)
        try:
            file = open(f"{filename}.zip", 'rb')
            # if ftp_sess != '':
            #     files = []
            #     ftp.dir(files.append)
            #     print(files)
        except FileNotFoundError:
            pass
        except UnboundLocalError:
            pass
            session.storbinary(f'STOR {filename}.zip', file)
            file.close()
            session.quit()
    # DEPRECIATED
    # if ftp_send:
    #     session = FTP(ftp_addr, ftp_user, ftp_pass)
    #     file = open(filename + '.zip', 'rb')  # file to send
    #     session.storbinary('STOR {}'.format(filename + '.zip'), file)  # send the file
    #     file.close()  # close file and FTP
    #     session.quit()


class State:
    class Client:
        player_obj = ""
        parachute = ""
    
    class FileWrite:
        discover_unit = False

    class GameState:
        TITLE_HANG = "War Thunder"
        TITLE_LOAD = "War Thunder - Loading"
        TITLE_BATT = "War Thunder - In battle"
        TITLE_DRIV = "War Thunder - Test Drive"
        TITLE_TEST = "War Thunder - Test Flight"
        TITLE_WAIT = "War Thunder - Waiting for game"
        TITLE_DX32 = "War Thunder (DirectX 11, 32bit) - In battle"
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


last_id_msg = 0
last_id_evt = 0
last_id_dmg = 0

unit_lookup = get_unit()
ntp = ntplib.NTPClient()
tick0 = time.perf_counter()
players_uid, players_cid = userinfo.get_basic_info()


# LOOP: MAIN
while True:

    # SIGINT: INIT
    signal(SIGINT, handler)

    # DISCOVER: WINDOW TITLE
    curr_game_state = window_title()

    # PROGRAM STATE: IN HANGAR
    if curr_game_state == State.GameState.TITLE_HANG:

        # STDOUT: RETURNED TO HANGAR
        if not State.Messages.hangar:
            nxt_batt()
            loguru.logger.info("[S] IDLE @ HANGAR: JOIN (TEST|BATTLE|CUSTOM)")
            State.Messages.hangar = True

        # STDOUT: RECORDING FINISHED
        if not State.Messages.rec_end:
            loguru.logger.info("[R] THUNDERTAC RECORDING HAS TERMINATED")
            State.Messages.rec_end = True

    # PROGRAM STATE: TEST FLIGHT
    elif curr_game_state == State.GameState.TITLE_TEST:

        # CHECK: LOCATION DATA
        if not State.Map.information:
            lati_m, long_m, map_area, temp_db = area_init()
            if lati_m is not None and long_m is not None:
                State.Map.information = True
        State.Recorder.sortie_header = False
        State.Recorder.active = True
        time_rec_start = time.time()

    # PROGRAM STATE: IN BATTLE
    elif curr_game_state == State.GameState.TITLE_BATT:

        # CHECK: LOCATION DATA
        if not State.Map.information:
            lati_m, long_m, map_area, temp_db = area_init()
            if lati_m is not None and long_m is not None:
                State.Map.information = True
                
        if not State.Messages.trigger_chat:
            loguru.logger.info(f"[R] GAMECHAT WAIT: Waiting for '{ttac_mas}' to trigger the recording")
            State.Messages.trigger_chat = True

        if State.Recorder.gamechat_start:
            if State.Map.information:  # and State.Messages.trigger_chat is False:
                if ttac_dbg:
                    loguru.logger.debug("[T] DEBUG TRIGGER RECOGNIZED")
                    time_rec_start = time.time()
                    loguru.logger.info("[R] RECORDING STARTED")
                    loguru.logger.debug("[R] TIME:" + str(time_rec_start))
                    State.Recorder.sortie_header = False
                    State.Recorder.active = True
                try:
                    gamechat_req = gamechat()
                    list_msglog = gamechat_req
                    if list_msglog:
                        last_msg = list_msglog[-1]["msg"]
                        last_mode = list_msglog[-1]["mode"]
                        last_sender = list_msglog[-1]["sender"]
                        if last_msg == ttac_rec:
                            if last_sender == ttac_mas:
                                State.Messages.trigger_chat = True
                                loguru.logger.debug("[T] MESSAGE TRIGGER RECOGNIZED")
                                time_rec_start = time.time()
                                loguru.logger.info("[R] RECORDING STARTED")
                                loguru.logger.debug("[R] TIME:" + str(time_rec_start))
                                State.Recorder.sortie_header = False
                                State.Recorder.active = True
                except requests.exceptions.ReadTimeout as e:
                    loguru.logger.error(e)

    while State.Recorder.active:

        if window_title() == State.GameState.TITLE_HANG:
            nxt_sort()
            inspector()
            nxt_batt()
            inspector()
            break

        try:
            map_objects = get_web_reqs(constants.WebAPI.OBJT)
        except json.decoder.JSONDecodeError as e:
            loguru.logger.exception(str(e))

        if map_objects and not State.Recorder.header_placed:
            filename = set_filename()
            insert_header(map_area, get_utc_offset())
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

                with open("ACMI/{}.acmi".format(filename), "a", encoding="utf8", newline="") as g:
                    g.write("#{}".format(time_adjusted_tick) + "\n")
                    g.write("-" + State.Client.player_obj + "\n")
                    g.write("0,Event=Destroyed|" + State.Client.player_obj + "|" + "\n")
                    if z > 15 and ias > 100:
                        State.Client.parachute = set_user_object()
                        parachute_align_gravity = time_adjusted_tick + 3
                        parachute_touchdown_time = (parachute_down(z) + parachute_align_gravity)
                        g.write(
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                            "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                                time_adjusted_tick, State.Client.parachute, x, y, z, r, p, h, z
                            )
                        )
                        g.write(
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                            "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                                parachute_align_gravity, State.Client.parachute, x, y, z - 15, 0, 0, h, z - 15,
                            )
                        )
                        g.write(
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                            "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                                parachute_touchdown_time, State.Client.parachute, x, y, 0, 0, 0, h, 0,
                            )
                        )
                        g.write(
                            "#{:0.2f}\n-{}\n0,Event=Destroyed|{}|\n".format(
                                parachute_touchdown_time,
                                State.Client.parachute,
                                State.Client.parachute,
                            )
                        )
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

        try:
            temp_test = gaijin_state_method()
            ind = get_web_reqs(constants.WebAPI.INDI)
            sta = get_web_reqs(constants.WebAPI.STAT)
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
                        ind = get_web_reqs(constants.WebAPI.INDI)
                        try:
                            if temp_test == "playing":
                                r = ind["aviahorizon_roll"] * -1
                                p = ind["aviahorizon_pitch"] * -1
                        except KeyError as err_plane_not_compatible:
                            if gaijin_state_method() == "playing":
                                loguru.logger.error("[P] This plane is not supported")
                        if not State.Recorder.discover_unit:
                            unit = ind["type"]
                            try:
                                loguru.logger.info("[P] UNIT RE-SPAWN: {}".format(unit_lookup[unit]['full']))
                            except KeyError:
                                loguru.logger.error("[D] ENTRY MISSING: {}".format(unit))
                                loguru.logger.info("[P] UNIT RE-SPAWN: {}".format(unit))
                            State.Recorder.discover_unit = True
                    except Exception as err:
                        print(err)
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

                    if not run_once_per_spawn:
                        fname, lname, sname = unit_lookup[unit].values()
                        run_once_per_spawn = True

                    sortie_telemetry = (
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},".format(
                                time_adjusted_tick, State.Client.player_obj, x, y, z, r, p, h
                            )
                            + "Throttle={},".format(s_throttle1)
                            + "RollControlInput={},".format(stick_ailerons)
                            + "PitchControlInput={},".format(stick_elevator)
                            + "YawControlInput={},".format(pedals)
                            + "IAS={:0.6f},".format(ias)
                            + "TAS={:0.6f},".format(tas)
                            + "FuelWeight={},".format(fuel_kg)
                            + "Mach={},".format(m)
                            + "AOA={},".format(aoa)
                            + "FuelVolume={},".format(fuel_vol)
                            + "LandingGear={},".format(gear)
                            + "Flaps={},".format(flaps)
                        # + "PilotHeadRoll={},".format(PilotHeadRoll)
                        # + "PilotHeadPitch={},".format(PilotHeadPitch)
                        # + "PilotHeadYaw={},".format(PilotHeadYaw)
                    )

                    sortie_subheader = (
                            "Slot={},".format("0")
                            + "Importance={},".format("1")
                            + "Parachute={},".format("0")
                            + "DragChute={},".format("0")
                            + "Disabled={},".format("0")
                            + "Pilot={},".format(ttac_usr)
                            + "Name={},".format(unit)
                            + "ShortName={},".format(unit_lookup[unit]['short'])
                            + "LongName={},".format(unit_lookup[unit]['long'])
                            + "FullName={},".format(unit_lookup[unit]['full'])
                            + "Type={},".format("Air+FixedWing")
                            + "Color={},".format("None")
                            + "Callsign={},".format("None")
                            + "Coalition={},".format("None")
                    )

                    with open("ACMI/{}.acmi".format(filename), "a", encoding="utf8", newline="") as g:
                        if not State.Recorder.sortie_header:
                            try:
                                g.write(sortie_telemetry + sortie_subheader + "\n")
                            except UnicodeEncodeError as err:
                                print(err)
                            State.Recorder.sortie_header = True
                        else:
                            g.write(sortie_telemetry + "\n")
            except KeyError as err:
                print(err)
            except TypeError as err:
                if State.Recorder.active:
                    pass

        except json.decoder.JSONDecodeError as e:
            loguru.logger.exception(str(e))
        except (TypeError, NameError) as e:
            loguru.logger.exception(str(e))
        except KeyError as e:
            loguru.logger.exception(str(e))
