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

FOR /f "delims=" %%I IN ('%PYPATH%\python.exe --version') DO SET "output=%%I"
(ECHO %output% | FINDSTR /i /c:"Python 3.7.4" >NUL) && (GOTO PythonAlreadyExisted)|| (GOTO PythonDoesNotExistOrWrongVerison)


:PythonDoesNotExistOrWrongVerison
CLS
ECHO. 
ECHO This .bat script will spawn an instance of Powershell with the Execution Policy bypassed.
ECHO For more information visit https:/go.microsoft.com/fwlink/?LinkID=135170
ECHO.
TIMEOUT /T 10
ECHO.
ECHO It will then call a .ps1 script to download and silently install Python 3.7.4 to
IF %_os_bitness% == 64 (
  ECHO %LOCALAPPDATA%\Programs\Python\Python37
) ELSE (
  ECHO %LOCALAPPDATA%\Programs\Python\Python37-32
)
ECHO.
TIMEOUT /T 10
ECHO.
Powershell -ExecutionPolicy Bypass -File "ignore.ps1"
ECHO.
ECHO.
GOTO PythonNowExists


:PythonAlreadyExisted
ECHO Python 3.7.4 x%_os_bitness% has already been installed.
TIMEOUT /T 5
GOTO PythonRequirements


:PythonNowExists
ECHO Python 3.7.4 x%_os_bitness% installation complete.
TIMEOUT /T 5
GOTO PythonRequirements

:PythonRequirements
CLS
IF %_os_bitness% == 64 (
  PYPATH=%LOCALAPPDATA%\Programs\Python\Python37
) ELSE (
  PYPATH=%LOCALAPPDATA%\Programs\Python\Python37-32
)
%PYPATH%\python -m venv venv
ECHO VIRTUAL ENVIRONMENT 'VENV' CREATED
CALL venv\Scripts\activate.bat
ECHO VIRTUAL ENVIRONMENT 'VENV' ACTIVATED
python -m pip install --upgrade pip
ECHO PIP PACKAGE INSTALLATION MANAGER UPGRADED
pip install -r requirements.txt
ECHO FETCHING AND INSTALLING REQUIRED PYTHON PACKAGES FOR OPERATION
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
ECHO FETCHING AND INSTALLING REQUIRED PYTHON PACKAGES FOR BUILDING/FREEZING
python getpywin32.py
ECHO PYWIN32-227 DOWNLOADED
easy_install pywin32-227.exe
ECHO PYWIN32-227 INSTALLED
DEL pywin32-227.exe
ECHO PYWIN32-227 CLEANED UP
PAUSE
ECHO EXIT NOW UNLESS YOU WANT TO RUN THE BUILD PROCESS
TIMEOUT /T 10
CALL build.bat
