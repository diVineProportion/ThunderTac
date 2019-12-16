import platform


def information_gathering(developer=False):
    """various information gathering for """
    if developer:
        version       = platform.python_version()
        version_tuple = platform.python_version_tuple()
        compiler      = platform.python_compiler()
        build         = platform.python_build()
    system       = platform.system()
    node         = platform.node()
    release      = platform.release()
    version      = platform.version()
    machine      = platform.machine()
    processor    = platform.processor()
    architecture = platform.architecture()

    return system, architecture[0]


if __name__ == "__main__":
    print("\n", "This module is not intended to be exectuted directly.", sep="")
    print("Also, not really a good idea to run somethign without looking at it first.")
    input("\n" + "Press the any key to exit.")

