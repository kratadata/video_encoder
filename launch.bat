@echo off
cd /d %~dp0
call encode\Scripts\activate
python app.py
pause
