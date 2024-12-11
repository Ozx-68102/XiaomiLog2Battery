@echo off
setlocal EnableDelayedExpansion
cd %~dp0

echo Welcome to use XiaomiLog2Battery project.
echo It will be run soon after some basic checks.

echo Checking Python Version...
REM Step 1: Check Python version
for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
set PYTHON_VERSION=%PYTHON_VERSION:~7,4%

if "%PYTHON_VERSION%" == "" (
    for /f "delims=" %%i in ('py -3.13 --version 2^>^&1') do set PYTHON_VERSION=%%i
    set PYTHON_VERSION=%PYTHON_VERSION:~7,4%
)

if "%PYTHON_VERSION:~0,4%" neq "3.13" (
	for /f "delims=" %%i in ('py -3.13 --version 2^>^&1') do set PYTHON_VERSION=%%i
    set PYTHON_VERSION=%PYTHON_VERSION:~7,4%
)

REM Check if the Python version starts with 3.13
if "%PYTHON_VERSION:~0,4%" neq "3.13" (
    echo Oops! Your python version in your system currently is %PYTHON_VERSION%.
	echo But you need at least Python 3.13 to run this program.
    echo Please install it on the official website below:
	echo https://www.python.org/downloads/release/python-3130/
	echo and set it in environment variables of your Windows.
    pause
    exit /b
)

echo Current Python version: %PYTHON_VERSION%
echo OK.


echo Checking venv folder
REM Step 2: Check if .venv exists
if exist ".venv" (
    where /r .venv * >nul 2>&1
    if %errorlevel% neq 0 (
        echo .venv is empty. Removing and recreating venv folder...
        rmdir /s /q .venv
        python -m venv .venv
    ) else (
		echo venv folder exists.
	)
) else (
	echo Creating venv folder...
    python -m venv .venv
)
echo OK.

echo Now preparing to activate virtual environment.
pause

REM Step 3: Activate the virtual environment
call .\.venv\Scripts\activate
echo Virtual environment was activated.

REM Step 4: Check for required libraries (only third-party)
echo Try to check for required libraries.
python .\Check_packages.py
if %errorlevel% neq 0 (
    echo Python script to check packages failed.
    pause
    exit /b
)

echo Checks completed. Program will be run soon.

REM Step 5: Run the Central.py script
python .\Central.py

REM Deactivate virtual environment after the script runs
call .\.venv\Scripts\deactivate
echo Program ran successfully so the virtual environment was deactivated.
pause