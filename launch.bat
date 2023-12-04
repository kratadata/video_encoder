@echo off
cd /d %~dp0
call a2v\Scripts\activate
python app.py
pause