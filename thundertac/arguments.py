import argparse
import sys

keyVal = 'Console'

parser = argparse.ArgumentParser()

parser.add_argument('-b', '--bypass', required=False, default=False, help="bypass check for updates", action='store_true')
parser.add_argument('-c', '--config', required=False, default=None, help="open the configuration file for editing", action='store_true')
parser.add_argument('-d', '--debug', choices=['T', 'F'], required=False, default=None, help="run in debug mode")
parser.add_argument('-q', '--quickedit', choices=['T', 'F'], required=False, default='F', help="do not disable QuickEdit mode for cmd.exe (default=F)")
parser.add_argument('-v', '--verbose', choices=['T', 'F'], required=False, default=None, help="")

args, unknown = parser.parse_known_args()


if not args.bypass:
    pass

if args.config:
    sys.exit(0)

if args.debug:
    input("press any key to continue")

if args.verbose:
    print("not yet implemented")
    input("press any key to continue")

if args.quickedit == 'F':
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)
    winreg.SetValueEx(key, "QuickEdit ", 0, winreg.REG_SZ, "0")
    winreg.CloseKey(key)
elif args.quickedit == 'T':
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)
    winreg.SetValueEx(key, "QuickEdit ", 0, winreg.REG_SZ, "1")
    winreg.CloseKey(key)