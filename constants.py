# see note in state.py

# TODO: migrate anything realted to the following imports to userinfo module
import os
import glob
from os import getenv
from os import environ
from getpass import getuser

# THUNDERTAC VERSION
TT_VERSION = '0.0.1'

# CONSTANTS
CONVTO_MPS = 0.277778

# BROWSER MAP LOCATIONS
BMAP_ADDR = "localhost"
BMAP_PORT = 8111
BMAP_BASE = "http://{}:{}/".format(BMAP_ADDR, BMAP_PORT)
BMAP_STATE = "state"
BMAP_INDIC = "indicators"
BMAP_OBJTS = "map_obj.json"
BMAP_INFOS = "map_info.json"
BMAP_CHATS = "gamechat?lastId=" + str(-1)

# WINDOW TITLES
TITLE_BASE = "War Thunder"
TITLE_LOAD = "War Thunder - Loading"
TITLE_BATT = "War Thunder - In battle"
TITLE_DRIV = "War Thunder - Test Drive"
TITLE_TEST = "War Thunder - Test Flight"
TITLE_WAIT = "War Thunder - Waiting for game"
TITLE_DX32 = "War Thunder (DirectX 11, 32bit) - In battle"
# PLACEHOLDER = "War Thunder OpenGL"
# PLACEHOLDER = "War Thunder D3DX9"

# TODO: change to TITLE_LIST_ALL
LIST_TITLE = [TITLE_BASE, TITLE_LOAD, TITLE_BATT, TITLE_DRIV, TITLE_TEST, TITLE_WAIT, TITLE_DX32]
LIST_BATT = [TITLE_BATT, TITLE_DX32]
TITLE_LIST_REC = [TITLE_BATT, TITLE_DX32, TITLE_TEST]

# LOGURU MESSSAGES
JOIN_BATTLE = "GAMESTATE: IN HANGAR / LOBBY"
JOINED_BATT = "GAMESTATE: IN BATTLE"
JOINED_TEST = "GAMESTATE: IN TEST FLIGHT"
PLAYERS_OID = "PLAYER OBJECT DESTROYED"

# THUNDERTAC USER ID
PLAYERS_UID = getuser()
PLAYERS_CID = getenv('COMPUTERNAME')