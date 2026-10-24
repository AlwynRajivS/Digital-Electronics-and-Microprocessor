@echo off
title Synchronous Counter Design Assistant - EC2201
echo ======================================================================
echo   Synchronous Counter Design Assistant - Launching Application
echo   Course: EC2201 Unit III - Synchronous Sequential Circuits
echo   Student: Sabariayyan P (Section B)
echo ======================================================================
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not added to PATH.
    pause
    exit /b 1
)

echo.
echo Starting Web Server on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
