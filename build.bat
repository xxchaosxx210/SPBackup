@REM This will build from source into an Exe

pyinstaller --clean ^
-n SPBackup ^
--add-data "images\*;images" app.py