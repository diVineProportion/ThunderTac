import os
import sys
import wget

major = sys.version_info[0]
minor = sys.version_info[1]
arch = sys.version[-7:-2]

if arch == "AMD64":
    arch = "win-amd64"
else:
    arch = "win32"

url = "https://github.com/mhammond/pywin32/releases/download/b227/pywin32-227.{arch}-py{maj}.{min}.exe".format(
    arch=arch, maj=major, min=minor)

filename = wget.download(url)

os.rename(filename, "pywin32-227.exe")
