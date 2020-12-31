import csv
import json
import os
import sys
import winreg



def get_ver_info():  # TODO: test for cases list_possibilites[1:2]
    """get steam install directory from registry; use found path to read version file """
    list_possibilites = [
        [winreg.HKEY_CURRENT_USER, "SOFTWARE\\Gaijin\\WarThunder\\InstallPath"],
        [winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Valve\\Steam\\InstallPath"],
        [winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Valve\\Steam\\InstallPath"],
    ]
    for list_item in list_possibilites:
        hkey, reg_path = list_item[0], list_item[1]
        path, name = os.path.split(reg_path)
        try:
            with winreg.OpenKey(hkey, path) as key:
                pre_path = winreg.QueryValueEx(key, name)[0]
                if "Steam" in path:
                    pre_path = "{}\\SteamApps\\common\\War Thunder".format(pre_path)
                post_path = "content\\pkg_main.ver"
                version_file = os.path.join(pre_path, post_path)
                with open(version_file, "r") as frv:
                    return frv.read()
        except FileNotFoundError as err_ver_not_found:
            input("NOT FOUND!\nPRESS ANY KEY TO EXIT")
            sys.exit()

def main(version):
    filename = f"D:\\WarThunderRepo\\{version}\\lang.vromfs.bin_u\\lang\\units.csv"

    # read csv
    if not os.path.isfile(filename):
        print(f"CURRENT GAME VERSION {version} DOES NOT MATCH UNPACKED VERSION")
        version = input(f"MANUAL ENTRY OF LAST KNOWN UNPACKED VERSION: ")
        filename = f"D:\\WarThunderRepo\\{version}\\lang.vromfs.bin_u\\lang\\units.csv"

    master = {"version": version, "units": {}}

    with open(filename, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        # row by row
        for row in csv_reader:
            if row[0][-2] == '_':
                # get key name
                wtid = row[0][:-2]
                # get values
                if row[0][-2:] == '_0':
                    a = row[1]
                elif row[0][-2:] == '_1':
                    b = row[1]
                elif row[0][-2:] == '_2':
                    c = row[1]
            # update master dict
            try:
                master['units'].update({wtid: {'full': a, 'long': b, 'short': c}})
            except NameError:
                pass

    with open('wtunits.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=4)

    master['units'].clear()


if __name__ == "__main__":
    version = get_ver_info()
    main(version)
