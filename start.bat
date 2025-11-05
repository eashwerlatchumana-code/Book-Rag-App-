@echo off
REM Startup script for RAG Chat Backend API (Windows)

echo Starting RAG Chat Backend API...
echo ================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Please create a .env file with your API keys
    echo.
)

REM Start the server
echo Starting FastAPI server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

python main.py
