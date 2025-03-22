@echo off
REM --- Load your working directory---
cd /D "D:\Users\ecuad\Projects\WebScraper"
SET logfile=batch.log

echo Starting Script at %date% %time% >> "%logfile%"

REM --- Load .env file ---
SET "filename=.env"

REM Check if .env exists
if not exist "%filename%" (
    echo [ERROR] .env file not found! >> "%logfile%"
    exit /b 1
)

REM Load variables from .env
for /F "usebackq tokens=1* delims== eol=#" %%a in ("%filename%") do (
    echo Setting variable: %%a=%%b >> "%logfile%"
    set "%%a=%%b"
)

REM --- Activate Conda Environment, SET YOUR Conda environment or whereever your python .exe is ---
call "D:\Users\ecuad\anaconda3\Scripts\activate.bat" base

REM --- Run Python Script ---
python test.py >> "%logfile%" 2>&1

echo Script ended at %date% %time% >> "%logfile%"


pause