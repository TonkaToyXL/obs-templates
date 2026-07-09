@echo off
REM Start the mic-reactive overlay bridge (serves overlays + /level.json).
setlocal EnableExtensions
cd /d "%~dp0\.."

where py >nul 2>nul
if %ERRORLEVEL%==0 (set "BOOT=py -3") else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 required. Install from python.org then re-run start-bridge.bat
    exit /b 1
  )
  set "BOOT=python"
)

if not defined OBS_WS_URL set "OBS_WS_URL=ws://127.0.0.1:4455"

set "VENV=%CD%\bridge\.venv"
set "VENV_PYTHON=%VENV%\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
  "%VENV_PYTHON%" -c "import websockets" >nul 2>nul
  if errorlevel 1 (
    "%VENV_PYTHON%" -m pip install --upgrade websockets
  )
) else (
  %BOOT% -m venv "%VENV%"
  "%VENV_PYTHON%" -m pip install --upgrade websockets
)

echo Starting overlay bridge from %CD%
echo Port comes from branding.json / branding.user.json unless OBS_BRIDGE_PORT is set.
"%VENV_PYTHON%" "%CD%\bridge\orb-bridge.py"
if errorlevel 1 pause
