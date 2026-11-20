@echo off
REM CS2 Report Generator Batch File
REM This batch file makes it easy to run the CS2 report generator

echo.
echo ========================================
echo      CS2 Report Generator
echo ========================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python and add it to your PATH.
    pause
    exit /b 1
)

REM Check if required modules are installed
echo Checking required modules...
python -c "import plotly; import pandas; import numpy; print('All required modules found')" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required modules...
    pip install plotly pandas numpy
    if %errorlevel% neq 0 (
        echo Error: Failed to install required modules.
        pause
        exit /b 1
    )
)

echo.
echo Starting CS2 Report Generator...
echo.

REM Check if arguments are provided
if "%~1"=="" (
    echo Usage: run_report.bat ^<demo_file^> ^<player_name^>
    echo Example: run_report.bat demo.dem player1
    echo.
    echo Available demo files in current directory:
    dir /b *.dem 2>nul
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

if "%~2"=="" (
    echo Usage: run_report.bat ^<demo_file^> ^<player_name^>
    echo Example: run_report.bat demo.dem player1
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

REM Run the report generator with provided parameters
python report.py --demo "%~1" --player "%~2"

echo.
echo Report generation completed!
echo.
pause