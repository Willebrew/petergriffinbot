@echo off
echo ========================================
echo  PETER GRIFFIN MOLTBOOK AGENT
echo ========================================
echo.

cd /d "%~dp0"

if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please run setup_agent.py first to register your agent.
    echo.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Peter Griffin Agent...
echo Press Ctrl+C to stop the agent
echo.

python src\main.py

pause
