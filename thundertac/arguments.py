import argparse
import sys

verbose = False

parser = argparse.ArgumentParser()

parser.add_argument('-b', '--bypass', required=False, default=False, help="bypass check for updates", action='store_true')
parser.add_argument('-c', '--config', required=False, default=None, help="open the configuration file for editing", action='store_true')
parser.add_argument('-d', '--debug', choices=['T', 'F'], required=False, default=None, help="run in debug mode")
parser.add_argument('-q', '--quickedit', choices=['T', 'F'], required=False, default='T', help="disable QuickEdit mode for cmd.exe (default=T)")
parser.add_argument('-v', '--verbose', choices=['T', 'F'], required=False, default=None, help="")

args, unknown = parser.parse_known_args()


if not args.bypass:
    pass

if args.config:
    pass

if args.debug:
    pass

if args.verbose:
    pass


if args.quickedit == 'T':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
elif args.quickedit == "F":
    pass
