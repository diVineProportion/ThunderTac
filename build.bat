call venv\Scripts\activate.bat
pyinstaller -F main.spec
copy wtunits.json dist\
copy config.ini dist\
pause
