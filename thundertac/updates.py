import sys
import time

from pyupdater.client import Client
from tqdm import tqdm

from __init__ import __version__
from pyu_cfg.client_config import ClientConfig


def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    with tqdm(total=total) as progress_bar:
        progress_bar.update(downloaded)


# def show_changelog():
#     import requests
#     from rich import console
#     from rich import markdown
#
#     remote_changelog = 'https://raw.githubusercontent.com/diVineProportion/ThunderTacUpdates/main/CHANGELOG.md'
#     resp = requests.get(remote_changelog)
#     console = console.Console()
#     md = markdown.Markdown(resp.text)
#     console.print(md)
#     time.sleep(5)
#     return


def user_input():
    pass


if __name__ == "updates":

    client = Client(ClientConfig())
    client.refresh()
    client.add_progress_hook(print_status_info)
    APP_NAME = ClientConfig.APP_NAME
    update_object = client.update_check(name=APP_NAME,
                                        version=__version__,
                                        channel='stable',
                                        strict=True)

    if update_object is not None:

        # show_changelog()
        # print(update_object.name)
        # print(update_object.filename)
        # print(update_object.data_dir)
        # print(update_object.update_folder)
        # print(update_object.headers)
        # print(update_object.channel)
        # print(update_object.platform)
        # print(update_object.current_version)
        # print(update_object.latest)
        # print(update_object.app_name)

        update_object.download()

        if update_object.is_downloaded():
            update_object.extract_restart()


if __name__ == "__main__":
    sys.exit(0)
