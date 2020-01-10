# import cgitb

# cgitb.enable(format='text')
import sys
import trace
tracer = trace.Trace(trace=1, ignoredirs=(sys.prefix, sys.exec_prefix))

import configparser
import json
import math
import os
import random
import sys
import time
import urllib.request
import warnings

from winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
import zipfile
from ftplib import FTP
from tinydb import TinyDB
import arrow
import imagehash
import loguru
import ntplib
import requests
import win32gui
from PIL import Image
from pywinauto import ElementNotFoundError, Application

import constants
import userinfo
import state
import mapsinfo
from maphash import maps

try:
    import simplejson as json
except ImportError:
    import json
time_notification = 0

db = TinyDB('db.json')
config = configparser.ConfigParser()


config.read('config.ini')

ttac_usr = config['general']['ttac_usr']
ttac_mas = config['general']['ttac_mas']
ttac_str = config['general']['ttac_str']
ftp_send = config['ftpcred']['ftp_send']
ftp_addr = config['ftpcred']['ftp_addr']
ftp_user = config['ftpcred']['ftp_user']
ftp_pass = config['ftpcred']['ftp_pass']



filename = ""
gilrnsmr = None
""" 
    test flight has 2 modes; test flight mode and mission mode
    one of the following two will tell force recording when in the
    mission mode (which has same window title as ranked matches)
"""
mode_test = False
mode_debug = False

object_id = False
time_rec_start = None
synced_chat_start = True
player_fetch_fail = False
insert_sortie_subheader = True
run_once_per_spawn = False
# TODO: write function to automatically handle this; start false, set true individually, then reset at appropriate time.
displayed_wait_msg_start = False
displayed_game_state_base = False
displayed_game_state_batt = False
displayed_new_spawn_detected = False
displayed_recorder_stopped = True
got_map_info = False
x = y = z = r = p = h = None
ias = player = wt2lat = wt2long = None
unit = s_throttle1 = tas = fuel_kg = None
m = aoa = fuel_vol = gear = flaps = None

with open('wtunits.json', 'r', encoding='utf-8') as f:
    unit_lookup = json.loads(f.read())

# loguru.logger.add("file_{time}.log", level="ERROR", rotation="100 MB")


def get_ver_info():  # TODO: test for cases list_possibilites[1:2]
    """get steam install directory from registry; use found path to read version file """
    list_possibilites = [
        [HKEY_CURRENT_USER, "SOFTWARE\\Gaijin\\WarThunder\\InstallPath"],
        [HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Valve\\Steam\\InstallPath"],
        [HKEY_LOCAL_MACHINE, "SOFTWARE\\Valve\\Steam\\InstallPath"],
    ]
    for list_item in list_possibilites:
        hkey, reg_path = list_item[0], list_item[1]
        path, name = os.path.split(reg_path)
        try:
            with OpenKey(hkey, path) as key:
                pre_path = QueryValueEx(key, name)[0]
                if "Steam" in path:
                    pre_path = "{}\\SteamApps\\common\\War Thunder".format(pre_path)
                post_path = "content\\pkg_main.ver"
                version_file = os.path.join(pre_path, post_path)
                with open(version_file, "r") as frv:
                    return frv.read()
        except FileNotFoundError as err_ver_not_found:
            loguru.logger.debug(str(err_ver_not_found) + " key: {}".format(key))
            continue


def get_loc_info():  # FIXME: update to py3 requests or document why I used urllib.request instead of requests
    """Compare map from browser interface to pre-calculated map hash to provide location info."""
    urllib.request.urlretrieve("http://localhost:8111/map.img", "map.jpg")
    _hash = str(imagehash.average_hash(Image.open("map.jpg")))
    if _hash in maps.keys():
        return maps[_hash][:-4]
    else:
        return 'ERROR: "{}" NOT FOUND"'.format(_hash)


def get_utc_offset():
    """get difference between players local machine and NTP time server; use to sync players"""
    ntpreq = None
    wait_for_response = True
    while wait_for_response:
        try:
            ntpreq = ntp.request("pool.ntp.org")
            wait_for_response = False
        except ntplib.NTPException as get_msg_err:
            pass
    # time offset is the difference between the users clock and the worldwide time synced NTP protocol
    time_offset = (ntpreq.recv_time - ntpreq.orig_time + ntpreq.tx_time - ntpreq.dest_time) / 2
    # record start time is the client synced UTC starting time with the offset included.
    record_start_time = str(arrow.get(arrow.utcnow().float_timestamp + time_offset))[:-6]
    return record_start_time


def get_filename():
    # TODO: Move to userinfo module
    sdate, stime = (str(arrow.utcnow())[:-13]).replace(":", ".").split("T")
    ltime = str(arrow.now().format('HH:mm:ss')).replace(":", ".")
    return "DATE({})_UTC({})_LOC({})_{}@{}".format(sdate, stime, ltime, constants.PLAYERS_UID, constants.PLAYERS_CID)


def get_web_reqs(req_type):
    """request data from web interface"""
    wait_till_recv = False
    while not wait_till_recv:
        try:
            response = requests.get("http://localhost:8111/" + req_type, timeout=0.1)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.ReadTimeout as e:
            pass


def game_state():
    """Use win32api window handle titles to detect war thunder state"""
    # TODO: consider using xored clog file for more robust detection
    for window_titles in constants.LIST_TITLE:
        whnd = win32gui.FindWindowEx(None, None, None, window_titles)
        if not (whnd == 0):
            return window_titles


def hdg(dx, dy):
    """Fallback in case compass is missing from indicators pannel"""
    dx *= wt2long * -1
    dy *= wt2lat * -1
    return int(180 - (180 / math.pi) * math.atan2(dx, dy))


def parachute_down(init_altitude):
    """Control parachute decent rate"""
    # avg ROF for parachte = 20 km/h
    # 20km/1hr * 1hr/3600s * 1000m/1km = ~5.5m/1s
    # 5.5 too slow
    falltime = init_altitude * 2.5
    return falltime


def insert_header(reference_time):
    """Insertion of mandatory .acmi header data + valuable information for current battle"""

    header_mandatory = (
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
        datasrc=str(get_ver_info()),
        datarec=constants.TT_VERSION,
        reftime=reference_time,
        rectime=str(arrow.utcnow())[:-13],
        hdruser=constants.PLAYERS_UID,
        hdrhost=constants.PLAYERS_CID,
        hdtitle=(game_state()[14:]).title(),
        catgory="NOT YET IMPLEMENTED",
        briefin=get_loc_info().replace("_", " "),
        debrief="NOT YET IMPLEMENTED",
        hdstate=get_loc_info().replace("_", " "),
        comment=arrow.now().format()[:-6],
    )

    header_numb_prop = (
        "0,ReferenceLongitude={reflong}\n" 
        "0,ReferenceLatitude={reflati}\n"
    ).format(
        reflong="0",
        reflati="0"
    )

    with open("{}.acmi".format(filename), "a", newline="") as fah:
        fah.write(header_mandatory + header_text_prop + header_numb_prop)


def set_user_object():
    """Object ID assigner"""
    return hex(random.randint(0, int(0xFFFFFFFFFFFFFFFF)))[2:]


def make_active(current_wt_window_title):
    """Force war thunder to active window state"""
    try:
        make_active_app = Application().connect(
            title=current_wt_window_title, class_name="DagorWClass"
        )
        make_active_app.DagorWClass.set_focus()
    except ElementNotFoundError:
        print("Please start war thunder\n")
        input("press any key to exit")
        exit()


def get_map_info():
    """Gather map information; very important for proper scaling"""
    # TODO: tank/plane switch causes map scale to change
    # TODO: create function with db lookup to place wt maps over real world 3d terrain
    mapsinfo.mainfunc()
    while True:
        try:
            inf = get_web_reqs(constants.BMAP_INFOS)
            map_max = inf["map_max"]
            map_min = inf["map_min"]
            map_total_x = map_max[0] - map_min[0]
            map_total_y = map_max[1] - map_min[1]
            lat = map_total_x / 111302
            long = map_total_y / 111320
            break
        except (TypeError, NameError) as err_not_sure:
            loguru.logger.error(str(err_not_sure + "this should be safe to remove"))
    return lat, long


def acmi_zip_out():
    pass
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except (ImportError, AttributeError):
        compression = zipfile.ZIP_STORED

    modes = {
        zipfile.ZIP_DEFLATED: 'deflated',
        zipfile.ZIP_STORED: 'stored',
    }

    print('creating archive')
    newname = get_loc_info() + '.jpg'
    if os.path.exists(newname):
        os.remove(newname)
    os.rename('map.jpg', newname)
    with zipfile.ZipFile(filename + '.zip', mode='w') as zf:
        mode_name = modes[compression]
        print('adding "{}" to archive using mode "{}"'.format(filename + '.acmi', mode_name))
        zf.write(filename + '.acmi', compress_type=compression)
        print('adding "{}" to archive using mode "{}"'.format(newname, mode_name))
        zf.write(newname, compress_type=compression)


def acmi_ftp_out():
    if ftp_send:
        session = FTP(ftp_addr , ftp_user, ftp_pass)
        file = open(filename + '.zip', 'rb')  # file to send
        session.storbinary('STOR {}'.format(filename + '.zip'), file)  # send the file
        file.close()  # close file and FTP
        session.quit()


def super_tracer(code_string, variable_state):
    logger.log("TRACER", "CODE: {}\n\t{}".format(code_string, variable_state))

''' def reset():
      global displayed_game_state_base
      global displayed_recorder_stopped
      global displayed_wait_msg_start
      global got_map_info
      curr_game_state = game_state()
      if curr_game_state == constants.TITLE_BASE:
          if not displayed_game_state_base:
              loguru.logger.info("STATE: In Hangar")
              displayed_game_state_base = True
          if state.loop_record is True and not displayed_recorder_stopped:
              loguru.logger.info("RECORD: Recording Stopped")
              displayed_recorder_stopped = True
          displayed_wait_msg_start = False
          state.loop_record = False
          got_map_info = False'''


warnings.filterwarnings("ignore")
ntp = ntplib.NTPClient()

loguru.logger.debug(str("PRGRM: module init completed"))
loguru.logger.debug(str("PRGRM: main loop running"))

from loguru import logger
logger.logger_tracer = logger.level("TRACER", no=38, color="<blue>", icon="🔍")
# x = logger.add(sys.stderr, format="{message}", level="INFO")
logger.log("TRACER", "MSG: STRING")

do_loop = True
while do_loop:
    # super_tracer("while do_loop:", do_loop)
    curr_game_state = game_state()
    if curr_game_state == constants.TITLE_BASE:
        if not displayed_game_state_base:
            loguru.logger.info("STATE: In Hangar")
            loguru.logger.info("PRGRM: Please join a match or test flight")
            displayed_game_state_base = True
        if not displayed_recorder_stopped:
            loguru.logger.info("RECORD: Recording Stopped")
            displayed_recorder_stopped = True
        displayed_wait_msg_start = False
        state.loop_record = False
        state.primary_header_placed = False
        got_map_info = False
    elif curr_game_state == constants.TITLE_TEST:
        time_rec_start = time.time()
        loguru.logger.debug("TIMER: Session Start=" + str(time_rec_start))
        if not got_map_info:
            wt2lat, wt2long = get_map_info()
            got_map_info = True
        loguru.logger.info("STATE: Test Flight")
        insert_sortie_subheader = True
        state.loop_record = True
    elif curr_game_state == (constants.TITLE_BATT or constants.TITLE_DX32):
        if not displayed_game_state_batt:
            loguru.logger.info("STATE: In Battle")
            displayed_game_state_batt = True
        if not got_map_info:
            wt2lat, wt2long = get_map_info()
            got_map_info = True
        if mode_debug:
            loguru.logger.debug(str("PRGRM: recording automatically started"))
            time_rec_start = time.time()
            # make_active(game_state())
            # loguru.logger.debug("WINDOW: Forced aces.exe to active window")
            state.loop_record = True
        elif synced_chat_start:
            if not displayed_wait_msg_start:
                loguru.logger.info("PRGRM: Wait for message start..")
                displayed_wait_msg_start = True
            if game_state() == constants.TITLE_BASE:
                state.loop_record = False
                displayed_game_state_base = False
                # displayed_recorder_stopped = False
                # reset()
            msg = get_web_reqs(constants.BMAP_CHATS)
            if msg:
                last_msg = msg[-1]["msg"]
                last_mode = msg[-1]["mode"]
                last_sender = msg[-1]["sender"]
                if last_msg == ttac_str:
                    if last_sender == ttac_mas:
                        loguru.logger.info("RECORD: String trigger recognized")
                        time_rec_start = time.time()
                        loguru.logger.debug("TIME: Session Start=" + str(time_rec_start))
                        # wt2lat, wt2long = get_map_info()
                        insert_sortie_subheader = True
                        state.loop_record = True

    while state.loop_record:
        if game_state() == constants.TITLE_BASE:
            state.loop_record = False
            state.loop_record = False
            displayed_game_state_base = False
            # displayed_recorder_stopped = False
            displayed_game_state_base = False
            state.loop_record = False
            got_map_info = False
            acmi_zip_out()
            acmi_ftp_out()
            if os.path.exists('map.jpg'):
                os.remove('map.jpg')
            db.insert({'time': arrow.utcnow().format(), 'map': get_loc_info() + '.jpg'})
        map_objects = None

        try:
            map_objects = get_web_reqs(constants.BMAP_OBJTS)
        except json.decoder.JSONDecodeError as err:
            # if game_state() == constants.TITLE_BASE:
            #     state.loop_record = False
            #     displayed_game_state_base = False
            #     displayed_recorder_stopped = False
            # else:
            pass

            # loguru.logger.exception(str(err))

        if map_objects and not state.primary_header_placed:
            filename = get_filename()
            insert_header(get_utc_offset())
            state.primary_header_placed = True

        time_this_tick = time.time()
        time_adjusted_tick = arrow.get(
            (time_this_tick - time_rec_start) - time_notification
        ).float_timestamp

        try:
            player = [el for el in map_objects if el["icon"] == "Player"][0]
        except (IndexError, TypeError) as err:
            try:
                player = [el for el in map_objects if el["icon"] == "Player"][0]
            except (IndexError, TypeError):
                pass
            else:
                continue
            player_fetch_fail = True
            # exception catches loss of player object on map_obj.json

            if state.PLAYERS_OID and player_fetch_fail and z is not None:
                # case: player already had object assigned and map_obj.json (player) update failed

                with open("{}.acmi".format(filename), "a", newline="") as g:
                    g.write("#{}".format(time_adjusted_tick) + "\n")
                    g.write("-" + state.PLAYERS_OID + "\n")
                    g.write("0,Event=Destroyed|" + state.PLAYERS_OID + "|" + "\n")
                    if z > 15 and ias > 100:
                        state.PARACHUTE = set_user_object()
                        parachute_align_gravity = time_adjusted_tick + 3
                        parachute_touchdown_time = (
                            parachute_down(z) + parachute_align_gravity
                        )
                        g.write(
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                            "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                                time_adjusted_tick, state.PARACHUTE, x, y, z, r, p, h, z
                            )
                        )
                        g.write(
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                            "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                                parachute_align_gravity, state.PARACHUTE, x, y, z - 15, 0, 0, h, z - 15,
                            )
                        )
                        g.write(
                            "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},Name=Parachute,"
                            "Type=Air+Parachutist,Coalition=Allies,Color=Blue,AGL={}\n".format(
                                parachute_touchdown_time, state.PARACHUTE, x, y, 0, 0, 0, h, 0,
                            )
                        )
                        g.write(
                            "#{:0.2f}\n-{}\n0,Event=Destroyed|{}|\n".format(
                                parachute_touchdown_time,
                                state.PARACHUTE,
                                state.PARACHUTE,
                            )
                        )
                    loguru.logger.debug("OBJECT: Player lost object: {}".format(state.PLAYERS_OID))
                    state.PLAYERS_OID = None
                    insert_sortie_subheader = True
                    displayed_new_spawn_detected = False
                    curr_game_state = game_state()
                    if curr_game_state == constants.TITLE_BASE:
                        loguru.logger.info("STATE: In Hangar")
                        displayed_game_state_base = False
                        state.loop_record = False
                        got_map_info = False
                        # TODO: INCO INTO RESET()
                        acmi_zip_out()
                        acmi_ftp_out()
                        if os.path.exists('map.jpg'):
                            os.remove('map.jpg')
                        db.insert({'time': arrow.utcnow(), 'map': get_loc_info()})
                    continue

            elif not state.PLAYERS_OID and player_fetch_fail:
                continue

        else:
            # player map_obj.json was successful so player is still alive
            player_fetch_fail = False

        if not state.PLAYERS_OID and not player_fetch_fail:
            # player doesn't have assigned object and map_obj was successful
            # time_bread = time.perf_counter()
            # set_msg_once(run_1, run_1[0], run_1[1], run_1[2])
            # time_toast = time.perf_counter()
            # time_notification = time_toast - time_bread
            state.PLAYERS_OID = set_user_object()
            loguru.logger.debug("OBJECT: Player assigned object: {}".format(state.PLAYERS_OID))
            # insert_sortie_subheader = True

        try:
            x = player["x"] * wt2lat
            y = player["y"] * wt2long * -1
        except NameError as err:
            print(err)

        try:
            sta = get_web_reqs(constants.BMAP_STATE)
            if sta is not None and sta["valid"]:
                z = sta["H, m"]
                ias = sta["IAS, km/h"] * constants.CONVTO_MPS
                tas = sta["TAS, km/h"] * constants.CONVTO_MPS
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

            ind = get_web_reqs(constants.BMAP_INDIC)
            try:
                if ind is not None and ind["valid"]:
                    try:
                        ind = get_web_reqs(constants.BMAP_INDIC)
                        try:
                            r = ind["aviahorizon_roll"] * -1
                            p = ind["aviahorizon_pitch"] * -1
                        except KeyError as err_plane_not_compatible:
                            print("This plane is currently not supported")
                        unit = ind["type"]
                        if not displayed_new_spawn_detected:
                            if unit_lookup[unit]:
                                loguru.logger.info("PLAYER: New spwan detected; UNIT: {}".format(
                                    unit_lookup[unit]['full'])
                                )
                            else:
                                loguru.logger.info("PLAYER: New spwan detected; UNIT: {}".format(unit))
                            displayed_new_spawn_detected = True
                    except KeyError:
                        pass
                        # TODO: Function to handle all non-existent or error prone indicator/state values
                    try:
                        pedals = ind["pedals"]
                    except KeyError as e:
                        pedals = ind["pedals1"]
                    stick_ailerons = ind["stick_ailerons"]
                    stick_elevator = ind["stick_elevator"]

                    try:
                        h = ind["compass"]
                    except KeyError as err:
                        h = hdg(player["dx"], player["dy"])

                    if not run_once_per_spawn:
                        with open('wtunits.json', 'r', encoding='utf-8') as fr:
                            unit_info = json.loads(fr.read())
                            fname, lname, sname = unit_info[unit].values()
                        run_once_per_spawn = True

                    sortie_telemetry = (
                        "#{:0.2f}\n{},T={:0.9f}|{:0.9f}|{}|{:0.1f}|{:0.1f}|{:0.1f},".format(
                            time_adjusted_tick, state.PLAYERS_OID, x, y, z, r, p, h
                        )
                        + "Throttle={}".format(s_throttle1)
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

                    with open("{}.acmi".format(filename), "a", newline="") as g:
                        if insert_sortie_subheader:
                            try:
                                g.write(sortie_telemetry + sortie_subheader + "\n")
                            except UnicodeEncodeError as err:
                                print(err)
                            insert_sortie_subheader = False
                        else:
                            g.write(sortie_telemetry + "\n")
            except TypeError as err:
                if state.loop_record:
                    pass
        except json.decoder.JSONDecodeError as e:
            loguru.logger.exception(str(e))
        except (TypeError, KeyError, NameError) as e:
            loguru.logger.exception(str(e))
