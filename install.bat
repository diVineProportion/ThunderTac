@ECHO OFF
ECHO.
ECHO.
ECHO Tasks
ECHO -----
ECHO.
ECHO 1. create venv
ECHO 2. activate venv
ECHO 3. update pip
ECHO 4. install (venv) python dependencies
ECHO 5. pip install (development) pyinstaller
ECHO 6. wget pywin32 extensions
ECHO 7. easy_install pywin32 extensions
ECHO.
ECHO.
pause
CLS
@ECHO ON
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
REM PyPI version has problems (v3.5) use development version from github (~v4.0)
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
wget https://github.com/mhammond/pywin32/releases/download/b227/pywin32-227.win-amd64-py3.7.exe
REM use easy install to install extensions in venv
easy_install pywin32-227.win-amd64-py3.7.exe
