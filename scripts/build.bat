@echo off

rem Build executable
pyinstaller --clean ^
-n SPBackup ^
-w ^
--add-data "images\*;images" ^
--icon .\images\SPBackup_icon.ico app.py
