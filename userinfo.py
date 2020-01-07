import platform
import time
import locale
import ctypes



def information_gathering(developer=False):
    """various information gathering for """
    if developer:
        # python information
        version       = platform.python_version()
        version_tuple = platform.python_version_tuple()
        compiler      = platform.python_compiler()
        build         = platform.python_build()

    # system information
    system       = platform.system()
    node         = platform.node()
    release      = platform.release()
    version      = platform.version()
    machine      = platform.machine()
    processor    = platform.processor()
    architecture = platform.architecture()


    # localization information
    timezone = time.tzname[time.localtime().tm_isdst]
    codepage = locale.getdefaultlocale()[1]
    localeui = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
    
    return system, architecture[0]



if __name__ == "__main__":
    print("\n", "This module is not intended to be exectuted directly.", sep="")
    print("Also, not really a good idea to run somethign without looking at it first.")
    input("\n" + "Press the any key to exit.")

