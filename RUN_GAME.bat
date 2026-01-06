@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo      FLAPPY BIRD PRO - REALISTIC EDITION
echo ===================================================
echo.

echo [1/3] Starting Backend Server...
start /B venv\Scripts\python.exe app.py > server_log.txt 2>&1

echo [2/3] Opening Dashboard...
timeout /t 5 >nul
start http://localhost:5000

echo [3/3] Launching Game...
echo.
echo CONTROLS:
echo - PINCH your Thumb and Index finger to Jump
echo - Keep index finger steady for better detection
echo - Press ESC in game to return to main menu
echo.

venv\Scripts\python.exe fp.py

echo.
echo Cleaning up...
taskkill /F /IM python.exe /T >nul 2>&1
echo Done.
pause
