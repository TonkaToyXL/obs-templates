@echo off
cd /d "%~dp0"
echo Installing TonkaToyXL OBS template...
where py >nul 2>nul && (py -3 install.py) || (where python >nul 2>nul && (python install.py) || (
  echo Python 3 required. See README.md for manual install.
  pause
  exit /b 1
))
echo.
pause
