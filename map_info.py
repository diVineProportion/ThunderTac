import json
import math
import os
import platform
import urllib.request

import simplejson
import PIL
import imagehash
import loguru
import numpy as np
import requests
from PIL import Image, ImageDraw
from requests import get
from requests.exceptions import ReadTimeout, ConnectTimeout
from xmltodict import unparse

from cfg import API

WebAPI = API()


maps = {
    '0x000000010383CFDF': 'arcade_norway_plain_map',
    '0x000000187EFEFC7C': 'avn_africa_gulf_tankmap',
    '0x000000C0F0FFFFFF': 'avg_africa_desert_tankmap',
    '0x000000F0F0F8FFFF': 'mozdok_map',
    '0x000003E6618FDFCF': 'avg_normandy_map',
    '0x00000C3C7DE11CC2': 'caribbean_islands_map',
    '0x0000183C3C1C0008': 'avn_coral_islands_map',
    '0x000018DC3C3FFF7B': 'air_afghan_map',
    '0x000040646EFF7F7F': 'avg_poland_map',
    '0x00007E7E7E7E3C00': 'avg_lazzaro_italy_tankmap',
    '0x0000C0C0B3FBFF3E': 'hurtgen_map',
    '0x000100010303C7DD': 'arcade_norway_green_map',
    '0x00016000F3FFFFB6': 'avg_berlin_tankmap',
    '0x00040E1EF8F03000': 'avn_fiji_map',
    '0x0004EC783C3F3DB8': 'avn_north_sea_tankmap',
    '0x002820E0E6CF9FFF': 'avg_snow_alps_tankmap',
    '0x0030787E3E3E5E00': 'air_race_phiphi_islands_map',
    '0x003C3C3E1C0E0600': 'arcade_tabletop_mountain_map',
    '0x003C3F3F1F3F3E00': 'arcade_africa_seashore_map',
    '0x003CF9F3F0E2F22C': 'avg_karpaty_passage_tankmap',
    '0x0080E0703F8F3FFF': 'avg_karpaty_passage_map',
    '0x00A076F0E2C03080': 'avn_fuego_islands_map',
    '0x00C00CB88CBCFCFF': 'korea_map',
    '0x00C0F0F8DCF8F8F0': 'avg_kursk_tankmap',
    '0x00D8DBF66E082606': 'avn_ireland_bay_map',
    '0x00F8FEFE3C3C1CE0': 'arcade_phiphi_crater_rocks_map',
    '0x01119883183EFFFE': 'avg_snow_alps_map',
    '0x011A3C7C7EFC7C08': 'avg_vietnam_hills_tankmap',
    '0x030F0E1C18182000': 'peleliu_map',
    '0x030F3FFCFCF0C0E3': 'avg_ardennes_map',
    '0x03377B7B83A7BF7F': 'avn_phang_nga_bay_islands_tankmap',
    '0x043C1C3870306040': 'saipan_map',
    '0x047C605E7777FCC0': 'arcade_phiphi_crater_map',
    '0x063F3F7F1E1E0000': 'avn_africa_gulf_map',
    '0x0707937F153CCC5D': 'kursk_map',
    '0x070F2C393D010707': 'avn_ice_port_tankmap',
    '0x0743181818E06230': 'iwo_jima_map',
    '0x0781814169E7F0FB': 'khalkhin_gol_map',
    '0x0787C7E3C3C0CBCF': 'avg_rheinland_map',
    '0x080080000000B9FF': 'avn_blacksea_port_tankmap',
    '0x080502071F1F0F8F': 'ruhr_map',
    '0x080C1C7C70707000': 'guam_map',
    '0x080C2700C0F0FF7F': 'guadalcanal_map',
    '0x080E0606607FCF40': 'avn_north_sea_map',
    '0x08187E7E7E7E1E02': 'avn_coral_islands_tankmap',
    '0x083C1E7C7870F0C0': 'avg_fulda_tankmap',
    '0x0C00476130FCFD0D': 'avg_japan_map',
    '0x0C3EFE78F87C1E0C': 'avg_alaska_town_tankmap',
    '0x0CCCFC7E7F7EFC18': 'avg_rheinland_tankmap',
    '0x0F6FFCF8FE781000': 'bulge_map',
    '0x112B19C024EF6206': 'avg_alaska_town_map',
    '0x14F4FCFCF8000001': 'britain_map',
    '0x170F1F7BF3F3BBF9': 'avg_finland_map',
    '0x181A72FCC5E1C103': 'avg_hurtgen_tankmap',
    '0x182070381E1E0000': 'malta_map',
    '0x183C3E3E3E1C0000': 'midway_map',
    '0x1F1F7F7F3F070301': 'port_moresby_map',
    '0x1FD3E0C8E8F4FBFF': 'arcade_snow_rocks_map',
    '0x2F07030080C1E3DF': 'avg_korea_lake_tankmap',
    '0x30FCC1E66E9FD8E0': 'arcade_mediterranean_map',
    '0x33363F3F3F333923': 'norway_map',
    '0x348283C39363FE3C': 'avg_hurtgen_map',
    '0x39C1033F3F0CC6D1': 'avn_norway_islands_tankmap',
    '0x3F0F1384D071383F': 'avg_sector_montmedy_map',
    '0x3F807EFCFEFCF0F1': 'avg_stalingrad_factory_tankmap',
    '0x3F9F47030363C7C4': 'arcade_alps_map',
    '0x3FFFDF3F77020001': 'avg_lazzaro_italy_map',
    '0x4604C0F0E8687078': 'avn_arabian_north_coast_tankmap',
    '0x4CCC1EFCFCBCFC20': 'avg_training_ground_tankmap',
    '0x5F0F0710188088FF': 'berlin_map',
    '0x5F392104CE5E5F54': 'avn_phang_nga_bay_islands_map',
    '0x6A681F9E1F0E463D': 'avn_alps_fjord_tankmap',
    '0x7020667717979BC3': 'avg_egypt_sinai_map',
    '0x70E4D0F008C0EC78': 'avn_arabian_north_coast_map',
    '0x70F8F8FE6E6F0200': 'honolulu_map',
    '0x003078783C1C8C08': 'honolulu_map',
    '0x7878FAF6FFEF80F0': 'avg_africa_desert_map',
    '0x7BDB8430607D88C4': 'arcade_rice_terraces_map',
    '0x7C3C1C0E2A0C1F1F': 'avg_eastern_europe_map',
    '0x7C7EFF1F1E1C0800': 'air_vietnam_map',
    '0x7D0D0C31B3030301': 'avg_mozdok_tankmap',
    '0x7EFFFFFFF7030100': 'avg_port_novorossiysk_map',
    '0x7F3F3F0F0707030F': 'avn_ice_port_map',
    '0x7FE7970303170707': 'avg_korea_lake_map',
    '0x8000E0E0C10F0F0F': 'dover_strait_map',
    '0x8080E0F4FEFFEDFF': 'avg_guadalcanal_tankmap',
    '0x80C48080C3DFBFFF': 'avg_ireland_tankmap',
    '0x860F1F0F0F00201F': 'water_map',
    '0x8F8F83C38181E0E0': 'arcade_canyon_snow_map',
    '0x8FC68480E6B6ACC7': 'avg_european_fortress_tankmap',
    '0x90E0E082F2FCFCFC': 'korsun_map',
    '0x9A9080FDEE00183E': 'avn_ice_field_tankmap',
    '0x9F3F5CD0E0B0121B': 'avg_american_valley_map',
    '0xB070E0E0C0C1CF9F': 'avg_krymsk_tankmap',
    '0xB8F8F0F0F030F8F8': 'avg_tunisia_desert_map',
    '0xBF3F878786100091': 'avg_volokolamsk_map',
    '0xC0C0E061FFFF7F7F': 'avn_blacksea_port_map',
    '0xC180183C3C180183': 'avn_fiji_tankmap',
    '0xC19110161F1F9FBF': 'avg_fulda_map',
    '0xC3433103A400836B': 'arcade_zhang_park_map',
    '0xC3C3C3C3FFFFFFFF': 'air_ladoga_map',
    '0xC9C7E70B331F3834': 'avn_norway_islands_map',
    '0xD000241C0087F7FF': 'avg_syria_map',
    '0xD90A0000E0F8F0F0': 'zhengzhou_map',
    '0xDFE0809061FFDFD0': 'avg_ardennes_tankmap',
    '0xE0E0C0C0C0CFFFFF': 'avg_japan_tankmap',
    '0xE0F7C4E4ED8210C0': 'avn_fuego_islands_tankmap',
    '0xE7EF9FB6F0F0F0E0': 'spain_map',
    '0xE8E020D8F880E07E': 'moscow_map',
    '0xEF0717381C20F0F0': 'avn_ireland_bay_tankmap',
    '0xF0E0C0C0C0C0E0F0': 'avg_karelia_forest_a_map',
    '0xF0F0F0A2030F1F0F': 'avg_poland_tankmap',
    '0xF0F83C3C190B1B1B': 'avn_ice_field_map',
    '0xF381480786024C06': 'avg_european_fortress_map',
    '0xF3F7FFC3C1E1C000': 'avg_abandoned_factory_tankmap',
    '0xF7EF4F4DE8F9FC3F': 'avg_volokolamsk_tankmap',
    '0xF7FEF9F8D8C08000': 'wake_island_map',
    '0xF8F87F7F3F070300': 'krymsk_map',
    '0xF8F8F03000000000': 'avn_mediterranean_port_tankmap',
    '0xF8F8F8F0E0E0E0E0': 'stalingrad_w_map',
    '0xF8F8F8F0F0F8FCFC': 'avg_egypt_sinai_tankmap',
    '0xF8F8F8F8F0F0F0F0': 'avn_england_shore_map',
    '0xFAF260C1E3333120': 'avg_abandoned_factory_map',
    '0xFC7E73F300070001': 'avg_eastern_europe_tankmap',
    '0xFCBCFEF8F87CFCE0': 'avg_karelia_forest_a_tankmap',
    '0xFCF0F0680CDE8800': 'arcade_norway_fjords_map',
    '0xFCF8F0E0FCFCFCFE': 'sicily_map',
    '0xFCFCD8E46C0E0080': 'arcade_africa_canyon_map',
    '0xFCFCFD9810BEFC0C': 'avg_american_valley_tankmap',
    '0xFCFEFDFF7E380001': 'avg_syria_tankmap',
    '0xFEFCFCF8D0C00000': 'avg_vietnam_hills_map',
    '0xFEFEFE00C0FEFEFE': 'avg_tunisia_desert_tankmap',
    '0xFF0340FFFFFF2000': 'avg_normandy_tankmap',
    '0xFF0F1F1F0F0F0A00': 'avg_sector_montmedy_tankmap',
    '0xFF13010307030301': 'avn_alps_fjord_map',
    '0xFFC0C0C08080383E': 'avn_england_shore_tankmap',
    '0xFFC300000000E3FF': 'arcade_asia_4roads_map',
    '0xFFF3F8F0C0C0F0F8': 'avg_port_novorossiysk_tankmap',
    '0xFFFC20C0D0C080E0': 'arcade_ireland_map',
    '0xFFFE1808081F1F3F': 'avg_finland_tankmap',
    '0xFFFFF9F8D8C0C000': 'wake_island_map',
    '0xFFFFFCF8E0000000': 'avn_mediterranean_port_map'
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
            urllib.request.urlretrieve(WebAPI.LMAP, 'map.jpg')
            map_obj = get(WebAPI.OBJT, timeout=0.02).json()
            inf_req = get(WebAPI.INFO, timeout=0.02).json()
            break
        except (json.decoder.JSONDecodeError) as e:
            pass
        except (ReadTimeout, ConnectTimeout) as e:
            pass
        except (simplejson.errors.JSONDecodeError) as e:
            pass

    image = Image.open('map.jpg')
    image_draw = ImageDraw.Draw(image)

    map_max = inf_req['map_max']
    map_min = inf_req['map_min']
    map_min_x, map_min_y = float(map_min[0]), float(map_min[1])
    map_max_x, map_max_y = float(map_max[0]), float(map_max[1])
    map_total = map_max_x - map_min_x
    map_total_x = map_max_x - map_min_x
    map_total_y = map_max_y - map_min_y

    grid_zero = inf_req['grid_zero']
    grid_step = inf_req['grid_steps']

    grid_zero_x, grid_zero_y = float(grid_zero[0]), float(grid_zero[1])
    grid_step_x, magrid_step_= float(grid_step[0]), float(grid_step[1])

    step_qnty = map_total / grid_step_x
    step_size = image.width / step_qnty
    step_offset = map_min_y - grid_zero_x

    if step_size == map_max_x:
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
    if platform.system() == "Windows":
        path = os.path.join(os.environ['APPDATA'], "Tacview\\Data\\Terrain\\Textures")
    elif platform.system() == "Linux":
        path = "/home/divine/Programs/Tacview (beta)/Data/Terrain/Textures/"

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
    inf_req = get(WebAPI.INFO, timeout=(0.02, 1)).json()
    map_max_m = inf_req['map_max']
    map_min_m = inf_req['map_min']
    grid_zero = inf_req['grid_zero']
    grid_step = inf_req['grid_steps']
    map_total = float(map_max_m[0]) - float(map_min_m[0])
    step_quantity = map_total / float(grid_step[0])
    map_total_x = float(map_max_m[0]) - float(map_min_m[0])
    map_total_y = float(map_max_m[1]) - float(map_min_m[1])
    map_generation = inf_req['map_generation']
    map_total_area = [map_total_x, map_total_y]
    loguru.logger.debug(f"[M] GENERATION No: {map_generation}")
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

    r = requests.get(WebAPI.LMAP, stream=True)
    r.raise_for_status()
    r.raw.decode_content = True
    with PIL.Image.open(r.raw) as img:
        img.save('map.jpg')
    r.close()

    _dict = {}
    percent_match = None
    # from browser map image, get md5 hash
    _hash = str(imagehash.average_hash(Image.open("map.jpg"))).upper()
    try:
        if show:
            loguru.logger.debug(f"[L] ACTUAL HASH  : 0x{_hash}")
        # lookup hash value against key from maps lookup dict
        match = maps[_hash]
    except KeyError:
        # if key not found
        for i in maps.keys():
            # calculate numerical difference between actual hash and values from maps lookup dict
            _dict[i] = levenshtein(_hash, i, ratio_calc=True)
        # iterating through each key (stored map hashes from maps lookup dict)
        for i in _dict.keys():
            # match the calculated difference to the max (or highest) calculated difference
            if _dict[i] == max(_dict.values()):
                match = maps[i]
                percent_match = _dict[i]
    finally:
        match = match[:-4].replace('_', ' ').title()
        for map_type in ['Avg', 'Avn', 'Air']:
            if map_type in match:
                match = match.replace(map_type, f"[{map_type.upper()}]")
        if show:
            loguru.logger.debug(f"[L] LOOKUP HASH  : 0x{_hash.upper()}")
            if percent_match:
                percent_match *= 100
                loguru.logger.debug(f"[L] LOOKUP MATCH : {str(percent_match)[:5]}%")
            else:
                loguru.logger.debug(f"[L] LOOKUP MATCH : 100.00%")
            loguru.logger.debug(f"[L] REGION IDENT : {match}")
        if os.path.exists('map.jpg'):
            os.remove('map.jpg')
        return match


# if __name__ == '__main__':
#     try:
#         main_def()
#         get_data()
#         get_info()
#     except urllib.error.URLError as e:
#         print(f'ERROR: {e}')
#         input('check aces.exe running and in match')
