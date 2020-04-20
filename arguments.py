import argparse
import os
import subprocess
import sys
import winreg

keyVal = 'Console'

parser = argparse.ArgumentParser()

parser.add_argument('-c', '--config', required=False, default=None, help="open the configuration file for editing")
parser.add_argument('-d', '--debug', choices=['T', 'F'], required=False, default=None, help="run in debug mode (forced record in battles")
parser.add_argument('-q', '--quickedit', choices=['T', 'F'], required=False, default='F', help="do not disable QuickEdit mode for cmd.exe (default=F")
parser.add_argument('-v', '--verbose', choices=['T', 'F'], required=False, default=None, help="generate crash logs for developer")

args, unknown = parser.parse_known_args()

if args.config:
    config_path = os.environ['LOCALAPPDATA'] + "\\warthunderapps\\thundertac\\update\\config.ini"
    subprocess.call(["notepad.exe", config_path])
    sys.exit(0)

if args.debug:
    print("not yet implemented")
    input("press any key to continue")

if args.verbose:
    print("not yet implemented")
    input("press any key to continue")

if args.quickedit == 'F':
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)
    winreg.SetValueEx(key, "QuickEdit ", 0, winreg.REG_SZ, "0")
    winreg.CloseKey(key)
elif args.quickedit == 'T':
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)
    winreg.SetValueEx(key, "QuickEdit ", 0, winreg.REG_SZ, "1")
    winreg.CloseKey(key)