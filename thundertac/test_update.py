from pyupdater.client import Client
from pyu_cfg.client_config import ClientConfig

APP_NAME = 'ThunderTac'
APP_VERSION = '0.0.1alpha-0'
APP_CHANNEL = 'beta'
APP_STRICT = True

def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)


client = Client(ClientConfig())
client.refresh()

client.add_progress_hook(print_status_info)

client = Client(ClientConfig(), refresh=True, progress_hooks=[print_status_info])

app_update = client.update_check(name=APP_NAME, version=APP_VERSION, channel=APP_CHANNEL, strict=APP_STRICT)

if app_update is not None:
    print("app_update.download()")