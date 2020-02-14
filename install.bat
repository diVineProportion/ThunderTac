@ECHO OFF
Set _os_bitness=64
IF %PROCESSOR_ARCHITECTURE% == x86 (
  IF NOT DEFINED PROCESSOR_ARCHITEW6432 Set _os_bitness=32
)

IF %_os_bitness% == 64 (
  SET PYPATH=%LOCALAPPDATA%\Programs\Python\Python37
) ELSE (
  SET PYPATH=%LOCALAPPDATA%\Programs\Python\Python37-32
)

FOR /f "delims=" %%I IN ('python.exe --version') DO SET "output=%%I"
(ECHO %output% | FINDSTR /i /c:"Python 3.7.4" >NUL) && (GOTO PythonAlreadyExisted)|| (GOTO PythonDoesNotExistOrWrongVerison)


:PythonDoesNotExistOrWrongVerison
CLS
ECHO. 
ECHO This .bat script will spawn an instance of Powershell with Execution Policy temporarily bypassed.
ECHO This will allow it run a Powershell script file that originated from a computer other that the one
ECHO you are currently working on. 
ECHO.
ECHO The .ps1 file will download and do a silent/background install of Python 3.7.4.
ECHO.
ECHO Installation Directory:
IF %_os_bitness% == 64 (
  ECHO %LOCALAPPDATA%\Programs\Python\Python37
) ELSE (
  ECHO %LOCALAPPDATA%\Programs\Python\Python37-32
)
ECHO.
ECHO.
ECHO For more information on Execution Policy visit https:/go.microsoft.com/fwlink/?LinkID=135170
ECHO.
PAUSE
ECHO.
Powershell -ExecutionPolicy Bypass -File "ignore.ps1"
ECHO.
ECHO.
GOTO PythonNowExists


:PythonAlreadyExisted
ECHO Python 3.7.4 x%_os_bitness% has already been installed.
ECHO.
TIMEOUT /T 5
GOTO PythonRequirements


:PythonNowExists
ECHO Python 3.7.4 x%_os_bitness% installation complete.
TIMEOUT /T 5
GOTO PythonRequirements

:PythonRequirements
CLS
IF %_os_bitness% == 64 (
  SET PYPATH=%LOCALAPPDATA%\Programs\Python\Python37
) ELSE (
  SET PYPATH=%LOCALAPPDATA%\Programs\Python\Python37-32
)

ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: python -m venv venv
ECHO -------------------------------------------------------------------------------------------------------------------
python -m venv venv
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : VIRTUAL ENVIRONMENT 'VENV' CREATED
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'CALL venv\Scripts\activate.bat'
ECHO -------------------------------------------------------------------------------------------------------------------
CALL venv\Scripts\activate.bat
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : VIRTUAL ENVIRONMENT 'VENV' ACTIVATED
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'python -m pip install --upgrade pip'
ECHO -------------------------------------------------------------------------------------------------------------------
python -m pip install --upgrade pip
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : PIP PACKAGE INSTALLATION MANAGER UPGRADED
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'pip install -r requirements.txt'
ECHO -------------------------------------------------------------------------------------------------------------------
pip install -r requirements.txt
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : REQUIRED PACKAGES INSTALLED TO 'VENV'
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz'
ECHO -------------------------------------------------------------------------------------------------------------------
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : PyInstaller Developer Branch INSTALLED TO 'VENV'
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'python getpywin32.py'
ECHO -------------------------------------------------------------------------------------------------------------------
python getpywin32.py
ECHO.
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : PYWIN32-227 DOWNLOADED
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'easy_install pywin32-227.exe'
ECHO -------------------------------------------------------------------------------------------------------------------
easy_install pywin32-227.exe
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : PYWIN32-227 INSTALLED TO 'VENV'
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO COMMAND: 'DEL pywin32-227.exe'
ECHO -------------------------------------------------------------------------------------------------------------------
DEL pywin32-227.exe
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STDOUT : 'pywin32-227.exe REMOVED
ECHO.
ECHO.
TIMEOUT /T 2
CLS
ECHO.
ECHO -------------------------------------------------------------------------------------------------------------------
ECHO STARTING FIRST TIME BUILD PROCESS
ECHO -------------------------------------------------------------------------------------------------------------------
TIMEOUT /T 10
CLS
CALL build.bat
