@echo off
echo Starting Automated Trading System...
echo.
echo This will run continuously and monitor markets automatically.
echo Press Ctrl+C to stop the system.
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the automated trading scheduler
python trading_scheduler.py

pause