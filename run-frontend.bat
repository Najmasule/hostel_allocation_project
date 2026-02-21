@echo off
set "NODEJS=C:\Program Files\nodejs"
set "PATH=%NODEJS%;%PATH%"
cd /d "%~dp0frontend"
"%NODEJS%\npm.cmd" install
"%NODEJS%\npm.cmd" run dev
