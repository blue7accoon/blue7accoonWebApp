@echo off
cd /d %~dp0
start /b Scripts\activate
TIMEOUT /T 2
set FLASK_ENV=development
set FLASK_APP=blue7accoon
echo.
echo ≈‰÷√“—ÕÍ≥…£°
echo.
flask init-db
flask run
