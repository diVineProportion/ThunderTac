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
    # print(downloaded, total, status)


if __name__ == "__main__":
    pass

if __name__ == "updates":

    client = Client(ClientConfig())
    client.refresh()
    client.add_progress_hook(print_status_info)
    APP_NAME = ClientConfig.APP_NAME
    update_object = client.update_check(name=APP_NAME,
                                        version=__version__,
                                        channel='strict',
                                        strict=True)

    if update_object is not None:
        update_object.download()

        if update_object.is_downloaded():
            update_object.extract_restart()




# import sys
# from pprint import pprint
#
# from config import CFG
# from pyu_cfg.client_config import ClientConfig
#
#
# def print_status_info(info):
#     total = info.get(u'total')
#     downloaded = info.get(u'downloaded')
#     status = info.get(u'status')
#     with tqdm(total=total) as progress_bar:
#         progress_bar.update(downloaded)
#     # print(downloaded, total, status)
#
#
# def initialization(_channel, _preferred_channel, _is_strict):
#     client = Client(ClientConfig())
#     client.refresh()
#     client.add_progress_hook(print_status_info)
#     app_name = ClientConfig.APP_NAME
#     app_version = __version__
#     return client.update_check(app_name, app_version, channel=_preferred_channel, strict=_is_strict)
#
#
# def get_archive_information(current):
#     try:
#         current = current.split('-')[2].replace('.zip', '')
#         channel_letter = current[-1]
#         if channel_letter == "a":
#             return current.split('a')[0], "alpha"
#         elif channel_letter == "b":
#             return current.split('b')[0], "beta"
#         else:
#             return "stable"
#     except AttributeError:
#         pass
#
#
# def update_check(_app_update, _verbose=False):
#     global displayed_version
#     if _app_update is not None:
#         try:
#             current_version, current_channel = get_archive_information(_app_update._current_archive_name)
#
#             if not displayed_version:
#                 print(f"THIS VERSION: {_app_update.app_name} v{current_version} ({current_channel}) ")
#                 displayed_version = True
#             print(f"There is an update available on the '{_app_update.channel}' channel")
#             if _verbose:
#                 pprint(vars(_app_update))
#         except TypeError:
#             pass
#         except UnboundLocalError:
#             pass
#
#
# def perform_update(_app_update):
#     if _app_update is not None:
#         _app_update.download()
#         if _app_update.is_downloaded():
#             _app_update.extract_restart()
#
#
# def get_clients_channel():
#     cfg = CFG()
#     cfg.read_cfg()
#     return cfg.cfg_pyu
#
#
# # channels = ['alpha', 'beta', 'stable']
# channels = ['stable']
# displayed_version = False
#
# channel = get_clients_channel()
