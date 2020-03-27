import csv
import json


def main():
    filename = "D:\\WarThunderRepo\\1.95.0.138\\lang.vromfs.bin_u\\lang\\units.csv"

    units = {}

    # read csv
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
                units.update({wtid: {'full': a, 'long': b, 'short': c}})
            except NameError:
                pass

    with open('wtunits.json', 'w', encoding='utf-8') as f:
        json.dump(units, f, ensure_ascii=False, indent=4)

    units.clear()


if __name__ == "__main__":
    main()
