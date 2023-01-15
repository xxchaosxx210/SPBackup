@REM This will build from source into an Exe

pyinstaller --clean ^
-n SPBackup ^
-w ^
--add-data "images\*;images" ^
--icon .\images\SPBackup_icon.ico app.py