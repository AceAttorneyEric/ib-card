@echo off
title Infinite Backlog Card Updater
cd /d "%~dp0"

echo.
echo ==========================================
echo   Infinite Backlog Card Updater
echo ==========================================
echo.

echo [1/2] Downloading recent game covers...
python download_recent_games.py

if errorlevel 1 goto error

echo.
echo [2/2] Generating card...
python generate_card.py

if errorlevel 1 goto error

echo.
echo ==========================================
echo   SUCCESS
echo ==========================================
echo.
echo Updated:
echo   output\ib-card.png
echo   docs\ib-card.png
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo   UPDATE FAILED
echo ==========================================
echo.
echo The process stopped before continuing.
echo Your existing card was not intentionally replaced
echo by any later step after the failure.
echo.
pause
exit /b 1