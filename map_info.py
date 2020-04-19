import json
import math
import os
import urllib.request

import PIL
import imagehash
import loguru
import numpy as np
import requests
from PIL import Image, ImageDraw
from requests import get
from requests.exceptions import ReadTimeout, ConnectTimeout
from xmltodict import unparse

import constants

debug_mode = False
informed = False

maps = {
    '000000010383cfdf': 'arcade_norway_plain_map',
    '000000187efefc7c': 'avn_africa_gulf_tankmap',
    '000000c0f0ffffff': 'avg_africa_desert_tankmap',
    '000000f0f0f8ffff': 'mozdok_map',
    '000003e6618fdfcf': 'avg_normandy_map',
    '00000c3c7de11cc2': 'caribbean_islands_map',
    '0000183c3c1c0008': 'avn_coral_islands_map',
    '000018dc3c3fff7b': 'air_afghan_map',
    '000040646eff7f7f': 'avg_poland_map',
    '00007e7e7e7e3c00': 'avg_lazzaro_italy_tankmap',
    '0000c0c0b3fbff3e': 'hurtgen_map',
    '000100010303c7dd': 'arcade_norway_green_map',
    '00016000f3ffffb6': 'avg_berlin_tankmap',
    '00040e1ef8f03000': 'avn_fiji_map',
    '0004ec783c3f3db8': 'avn_north_sea_tankmap',
    '002820e0e6cf9fff': 'avg_snow_alps_tankmap',
    '0030787e3e3e5e00': 'air_race_phiphi_islands_map',
    '003c3c3e1c0e0600': 'arcade_tabletop_mountain_map',
    '003c3f3f1f3f3e00': 'arcade_africa_seashore_map',
    '003cf9f3f0e2f22c': 'avg_karpaty_passage_tankmap',
    '0080e0703f8f3fff': 'avg_karpaty_passage_map',
    '00a076f0e2c03080': 'avn_fuego_islands_map',
    '00c00cb88cbcfcff': 'korea_map',
    '00c0f0f8dcf8f8f0': 'avg_kursk_tankmap',
    '00d8dbf66e082606': 'avn_ireland_bay_map',
    '00f8fefe3c3c1ce0': 'arcade_phiphi_crater_rocks_map',
    '01119883183efffe': 'avg_snow_alps_map',
    '011a3c7c7efc7c08': 'avg_vietnam_hills_tankmap',
    '030f0e1c18182000': 'peleliu_map',
    '030f3ffcfcf0c0e3': 'avg_ardennes_map',
    '03377b7b83a7bf7f': 'avn_phang_nga_bay_islands_tankmap',
    '043c1c3870306040': 'saipan_map',
    '047c605e7777fcc0': 'arcade_phiphi_crater_map',
    '063f3f7f1e1e0000': 'avn_africa_gulf_map',
    '0707937f153ccc5d': 'kursk_map',
    '070f2c393d010707': 'avn_ice_port_tankmap',
    '0743181818e06230': 'iwo_jima_map',
    '0781814169e7f0fb': 'khalkhin_gol_map',
    '0787c7e3c3c0cbcf': 'avg_rheinland_map',
    '080080000000b9ff': 'avn_blacksea_port_tankmap',
    '080502071f1f0f8f': 'ruhr_map',
    '080c1c7c70707000': 'guam_map',
    '080c2700c0f0ff7f': 'guadalcanal_map',
    '080e0606607fcf40': 'avn_north_sea_map',
    '08187e7e7e7e1e02': 'avn_coral_islands_tankmap',
    '083c1e7c7870f0c0': 'avg_fulda_tankmap',
    '0c00476130fcfd0d': 'avg_japan_map',
    '0c3efe78f87c1e0c': 'avg_alaska_town_tankmap',
    '0cccfc7e7f7efc18': 'avg_rheinland_tankmap',
    '0f6ffcf8fe781000': 'bulge_map',
    '112b19c024ef6206': 'avg_alaska_town_map',
    '14f4fcfcf8000001': 'britain_map',
    '170f1f7bf3f3bbf9': 'avg_finland_map',
    '181a72fcc5e1c103': 'avg_hurtgen_tankmap',
    '182070381e1e0000': 'malta_map',
    '183c3e3e3e1c0000': 'midway_map',
    '1f1f7f7f3f070301': 'port_moresby_map',
    '1fd3e0c8e8f4fbff': 'arcade_snow_rocks_map',
    '2f07030080c1e3df': 'avg_korea_lake_tankmap',
    '30fcc1e66e9fd8e0': 'arcade_mediterranean_map',
    '33363f3f3f333923': 'norway_map',
    '348283c39363fe3c': 'avg_hurtgen_map',
    '39c1033f3f0cc6d1': 'avn_norway_islands_tankmap',
    '3f0f1384d071383f': 'avg_sector_montmedy_map',
    '3f807efcfefcf0f1': 'avg_stalingrad_factory_tankmap',
    '3f9f47030363c7c4': 'arcade_alps_map',
    '3fffdf3f77020001': 'avg_lazzaro_italy_map',
    '4604c0f0e8687078': 'avn_arabian_north_coast_tankmap',
    '4ccc1efcfcbcfc20': 'avg_training_ground_tankmap',
    '5f0f0710188088ff': 'berlin_map',
    '5f392104ce5e5f54': 'avn_phang_nga_bay_islands_map',
    '6a681f9e1f0e463d': 'avn_alps_fjord_tankmap',
    '7020667717979bc3': 'avg_egypt_sinai_map',
    '70e4d0f008c0ec78': 'avn_arabian_north_coast_map',
    '70f8f8fe6e6f0200': 'honolulu_map',
    '7878faf6ffef80f0': 'avg_africa_desert_map',
    '7bdb8430607d88c4': 'arcade_rice_terraces_map',
    '7c3c1c0e2a0c1f1f': 'avg_eastern_europe_map',
    '7c7eff1f1e1c0800': 'air_vietnam_map',
    '7d0d0c31b3030301': 'avg_mozdok_tankmap',
    '7efffffff7030100': 'avg_port_novorossiysk_map',
    '7f3f3f0f0707030f': 'avn_ice_port_map',
    '7fe7970303170707': 'avg_korea_lake_map',
    '8000e0e0c10f0f0f': 'dover_strait_map',
    '8080e0f4feffedff': 'avg_guadalcanal_tankmap',
    '80c48080c3dfbfff': 'avg_ireland_tankmap',
    '860f1f0f0f00201f': 'water_map',
    '8f8f83c38181e0e0': 'arcade_canyon_snow_map',
    '8fc68480e6b6acc7': 'avg_european_fortress_tankmap',
    '90e0e082f2fcfcfc': 'korsun_map',
    '9a9080fdee00183e': 'avn_ice_field_tankmap',
    '9f3f5cd0e0b0121b': 'avg_american_valley_map',
    'b070e0e0c0c1cf9f': 'avg_krymsk_tankmap',
    'b8f8f0f0f030f8f8': 'avg_tunisia_desert_map',
    'bf3f878786100091': 'avg_volokolamsk_map',
    'c0c0e061ffff7f7f': 'avn_blacksea_port_map',
    'c180183c3c180183': 'avn_fiji_tankmap',
    'c19110161f1f9fbf': 'avg_fulda_map',
    'c3433103a400836b': 'arcade_zhang_park_map',
    'c3c3c3c3ffffffff': 'air_ladoga_map',
    'c9c7e70b331f3834': 'avn_norway_islands_map',
    'd000241c0087f7ff': 'avg_syria_map',
    'd90a0000e0f8f0f0': 'zhengzhou_map',
    'dfe0809061ffdfd0': 'avg_ardennes_tankmap',
    'e0e0c0c0c0cfffff': 'avg_japan_tankmap',
    'e0f7c4e4ed8210c0': 'avn_fuego_islands_tankmap',
    'e7ef9fb6f0f0f0e0': 'spain_map',
    'e8e020d8f880e07e': 'moscow_map',
    'ef0717381c20f0f0': 'avn_ireland_bay_tankmap',
    'f0e0c0c0c0c0e0f0': 'avg_karelia_forest_a_map',
    'f0f0f0a2030f1f0f': 'avg_poland_tankmap',
    'f0f83c3c190b1b1b': 'avn_ice_field_map',
    'f381480786024c06': 'avg_european_fortress_map',
    'f3f7ffc3c1e1c000': 'avg_abandoned_factory_tankmap',
    'f7ef4f4de8f9fc3f': 'avg_volokolamsk_tankmap',
    'f7fef9f8d8c08000': 'wake_island_map',
    'f8f87f7f3f070300': 'krymsk_map',
    'f8f8f03000000000': 'avn_mediterranean_port_tankmap',
    'f8f8f8f0e0e0e0e0': 'stalingrad_w_map',
    'f8f8f8f0f0f8fcfc': 'avg_egypt_sinai_tankmap',
    'f8f8f8f8f0f0f0f0': 'avn_england_shore_map',
    'faf260c1e3333120': 'avg_abandoned_factory_map',
    'fc7e73f300070001': 'avg_eastern_europe_tankmap',
    'fcbcfef8f87cfce0': 'avg_karelia_forest_a_tankmap',
    'fcf0f0680cde8800': 'arcade_norway_fjords_map',
    'fcf8f0e0fcfcfcfe': 'sicily_map',
    'fcfcd8e46c0e0080': 'arcade_africa_canyon_map',
    'fcfcfd9810befc0c': 'avg_american_valley_tankmap',
    'fcfefdff7e380001': 'avg_syria_tankmap',
    'fefcfcf8d0c00000': 'avg_vietnam_hills_map',
    'fefefe00c0fefefe': 'avg_tunisia_desert_tankmap',
    'ff0340ffffff2000': 'avg_normandy_tankmap',
    'ff0f1f1f0f0f0a00': 'avg_sector_montmedy_tankmap',
    'ff13010307030301': 'avn_alps_fjord_map',
    'ffc0c0c08080383e': 'avn_england_shore_tankmap',
    'ffc300000000e3ff': 'arcade_asia_4roads_map',
    'fff3f8f0c0c0f0f8': 'avg_port_novorossiysk_tankmap',
    'fffc20c0d0c080e0': 'arcade_ireland_map',
    'fffe1808081f1f3f': 'avg_finland_tankmap',
    'fffff9f8d8c0c000': 'wake_island_map',
    'fffffcf8e0000000': 'avn_mediterranean_port_map'
}


def levenshtein(s, t, ratio_calc=False):
    """
        Levenshtein distance is a string metric for measuring the
        difference between two sequences (or strings)
    """
    rows = len(s) + 1
    cols = len(t) + 1
    distance = np.zeros((rows, cols), dtype=int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0
            else:
                if ratio_calc:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row - 1][col] + 1,
                                     distance[row][col - 1] + 1,
                                     distance[row - 1][col - 1] + cost)
    if ratio_calc:
        ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        return ratio
    else:
        return "The strings are {} edits away".format(distance[row][col])


def pythag(a, b):
    """
        given: two legs of right triangle
        return: length of the hypotenuse
    """
    return math.sqrt((a ** 2) + (b ** 2))


def get_distance(x1, y1, x2, y2):
    """
        given: 2 points in R^2
        return: distance between points
    """
    return math.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))


def latlon2meters(lat1, lon1, lat2, lon2):
    """
        note: modified Haversine formula
        given: 2 (lat, long) pairs
        return: distance between the points
    """
    r = 6378.137
    d_lat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    d_lon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(
        lat2 * math.pi / 180) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c
    return d * 1000


def main_def():
    while True:
        try:
            urllib.request.urlretrieve('http://localhost:8111/map.img', 'map.jpg')
            map_obj = get('http://localhost:8111/map_obj.json', timeout=0.02).json()
            inf_req = get('http://localhost:8111/map_info.json', timeout=0.02).json()
            break
        except (json.decoder.JSONDecodeError) as e:
            pass
        except (ReadTimeout, ConnectTimeout) as e:
            pass

    image = Image.open('map.jpg')
    image_draw = ImageDraw.Draw(image)

    map_max = inf_req['map_max']
    map_min = inf_req['map_min']
    map_total = map_max[0] - map_min[0]
    map_total_x = map_max[0] - map_min[0]
    map_total_y = map_max[1] - map_min[1]

    grid_zero = inf_req['grid_zero']
    grid_step = inf_req['grid_steps']

    step_qnty = map_total / grid_step[0]
    step_size = image.width / step_qnty
    step_offset = map_min[0] - grid_zero[0]

    if step_size == map_max[0]:
        # TODO: document this, it was a hack fix for the odd maps that cause scale problems
        '''assuming duel map until found to be other'''
        step_offset = 0
        step_size = 256

    pixels_x, pixels_y = image.width, image.height

    x_start = 0
    y_start = 0
    x_end = pixels_x
    y_end = pixels_y

    for x in range(int(step_offset), int(image.width), int(step_size)):
        line = ((x, y_start), (x, y_end))
        image_draw.line(line, fill=256)

    for y in range(int(step_offset), int(image.width), int(step_size)):
        line = ((x_start, y), (x_end, y))
        image_draw.line(line, fill=256)

    af_list = [el for el in map_obj if el['type'] == 'airfield']
    for i in range(len(af_list)):
        afsx = af_list[i]['sx'] * pixels_x
        afsy = af_list[i]['sy'] * pixels_y
        afex = af_list[i]['ex'] * pixels_x
        afey = af_list[i]['ey'] * pixels_y
        acol = tuple(af_list[i]['color[]'])
        afln = get_distance(afsx, afsy, afex, afey)

        # prevent the aircraft carriers from being drawn as static objects
        if afln > 20:
            line = ((afsx, afsy), (afex, afey))
            image_draw.line(line, fill=acol, width=10)

    # if os.path.exists('map.jpg'):
    #     os.remove('map.jpg')

    # TODO: provide a standard .xml to display the custom textures
    # lat long (tacview) to mach (war thunder)
    # we are using a 1 x 1 (lat x long) grid south west of 0,0
    # (lat, long)

    UpperLeft = UL = (0, 0)
    LowerLeft = LL = (-1, 0)
    UpperRight = UR = (0, 1)
    LowerRight = LR = (-1, 1)

    map_name = get_info(show=True)

    tex_insert = {
        "Resources": {
            "CustomTextureList": {
                "CustomTexture": {
                    "File": f"{map_name}.jpg",
                    "Projection": "Triangle",
                    "BottomLeft": {
                        "Longitude": "0",
                        "Latitude": "-0.5888095854284137"
                    },
                    "BottomRight": {
                        "Longitude": "0.5887199046005696",
                        "Latitude": "-0.5888095854284137"
                    },
                    "TopRight": {
                        "Longitude": "0.5887199046005696",
                        "Latitude": "0"
                    },
                    "TopLeft": {
                        "Longitude": "0",
                        "Latitude": "0"
                    }
                }
            }
        }
    }

    # take away:
    # 1 latitudinal degree (in meters) is always the same
    # latlon2meters(lat0, lon0, lat1, lon1)

    # latlon2meters(0,0,-1,0)
    # >>> 111319.49079327357
    # latlon2meters(0,1,-1,1)
    # >>> 111319.49079327357

    # 1 longitudinal degree (in meters) is longer closer to the equator
    # length (in meters) of 1 longitudinal degree at 0 degrees of latitude
    # latlon2meters(0, 0, 0, 1)
    # >>> 111319.49079327357

    # length (in meters) of 1 longitudinal degree at 1 degrees of latitude
    # latlon2meters(-1, 0, -1, 1)
    # >>> 111302.53586533663

    scalar_lon_min = latlon2meters(0, 0, 0, 1)
    scalar_lon_max = latlon2meters(-1, 0, -1, 1)
    # these two are the same; kept for consistency
    scalar_lat_min = latlon2meters(0, 0, -1, 0)
    scalar_lat_max = latlon2meters(0, 1, -1, 1)

    tl_lat = 0
    tl_lon = 0

    bl_lat = map_total_y / scalar_lat_max * -1
    bl_lon = 0

    tr_lat = 0
    tr_lon = map_total_x / scalar_lon_max

    br_lat = map_total_y / scalar_lat_min * -1
    br_lon = map_total_x / scalar_lon_min

    tex_insert['Resources']['CustomTextureList']['CustomTexture']['BottomLeft']['Longitude'] = bl_lon
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['BottomLeft']['Latitude'] = bl_lat
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['BottomRight']['Longitude'] = br_lon
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['BottomRight']['Latitude'] = br_lat
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['TopLeft']['Longitude'] = tl_lon
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['TopLeft']['Latitude'] = tl_lat
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['TopRight']['Longitude'] = tr_lon
    tex_insert['Resources']['CustomTextureList']['CustomTexture']['TopRight']['Latitude'] = tr_lat

    # TODO: check for existing .xml and append rather than overwrite
    path = os.path.join(os.environ['APPDATA'], "Tacview\\Data\\Terrain\\Textures")

    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + '\\CustomTextureList.xml', 'w') as fw:
        fw.write(unparse(tex_insert, pretty=True))

    final_path = f"{path}\\{map_name}.jpg"
    if os.path.exists(final_path):
        os.remove(final_path)
    if os.path.exists(path):
        image.save(final_path)


def get_data():
    inf_req = get(constants.WebAPI.INFO, timeout=(0.02, 1)).json()
    map_max_m = inf_req['map_max']
    map_min_m = inf_req['map_min']
    grid_zero = inf_req['grid_zero']
    grid_step = inf_req['grid_steps']
    map_total = map_max_m[0] - map_min_m[0]
    step_quantity = map_total / grid_step[0]
    map_total_x = map_max_m[0] - map_min_m[0]
    map_total_y = map_max_m[1] - map_min_m[1]
    map_generation = inf_req['map_generation']
    map_total_area = [map_total_x, map_total_y]
    loguru.logger.debug(f"[M] GENERATION ##: {map_generation}")
    loguru.logger.debug(f"[M] LOCAL MAX (m): {map_max_m}")
    loguru.logger.debug(f"[M] LOCAL MIN (m): {map_min_m}")
    loguru.logger.debug(f"[M] MAP TOTAL (m): {map_total_area}")
    loguru.logger.debug(f"[M] GRID ZERO (m): {grid_zero}")
    loguru.logger.debug(f"[M] GRID STEP (m): {grid_step}")

    return map_total_area


def get_info(show=False):
    """
        given: when in active battle or test flight
        return: low resolution image of the location
    """

    r = requests.get(constants.WebAPI.LMAP, stream=True)
    r.raise_for_status()
    r.raw.decode_content = True
    with PIL.Image.open(r.raw) as img:
        img.save('map.jpg')
    r.close()

    # calculate the md5 hash and compare to a list of md5 hashes
    _dict = {}
    _hash = str(imagehash.average_hash(Image.open("map.jpg")))
    try:
        match = maps[_hash]
    except KeyError:
        for i in maps.keys():
            _dict[i] = levenshtein(_hash, i, ratio_calc=True)
        for i in _dict.keys():
            if _dict[i] == max(_dict.values()):
                match = maps[i]
    finally:
        match = match[:-4].replace('_', ' ').title()
        for map_type in ['Avg', 'Avn', 'Air']:
            if map_type in match:
                match = match.replace(map_type, f"[{map_type.upper()}]")
        if show:
            loguru.logger.debug(f"[L] REGION HASHED: 0x{_hash.upper()}")
            loguru.logger.debug(f"[L] REGION BINARY: {match}")
        if os.path.exists('map.jpg'):
            os.remove('map.jpg')
        return match


if __name__ == '__main__':
    try:
        main_def()
        get_data()
        get_info()
    except urllib.error.URLError as e:
        print(f'ERROR: {e}')
        input('check aces.exe running and in match')
