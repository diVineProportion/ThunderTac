@ECHO OFF
ECHO.
ECHO Would you like to create a build from scratch?
ECHO.
CHOICE /C YNC /T 5 /D N /N /M "[Y]es, [N]o or [C]ancel."
IF %ERRORLEVEL% EQU 3 GOTO:EOF
IF %ERRORLEVEL% EQU 2 GOTO BUILD
IF %ERRORLEVEL% EQU 1 GOTO CLEAN

:CLEAN
DEL /Q /S dist\
DEL /Q /S build\
DEL /Q /S __pycache__\

:BUILD
CALL venv\Scripts\activate.bat
pyinstaller -F main.spec
COPY wtunits.json dist\
COPY config.ini dist\
ECHO COMPLETE!
TIMEOUT /T 10
