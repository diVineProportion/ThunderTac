call venv\Scripts\activate.bat
pyinstaller -F main.spec
cp wtunits.json dist\
pause
