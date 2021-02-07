import os
import __init__

from pathlib import Path
parent = Path(__file__).resolve().parent
src = parent.joinpath('pyu-data/deploy')
des = parent.parent.parent.joinpath('ThunderTacUpdates')

os.system(f'pyupdater build --app-version={__init__.__version__} --pyinstaller-log-info pyu_cfg\win.spec')
os.system(f'pyupdater pkg --process --sign')
os.system(f'xcopy {src} {des} /Y')
os.system(f'cd ..\\ThunderTacUpdates')
os.system(f'git add *')
os.system(f'git commit -m "{__init__.__version__}"')
os.system(f'git push')



