@echo off
echo ========================================
echo Agent 86 - Setup Script
echo ========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)
echo Virtual environment created successfully.
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)
echo Virtual environment activated.
echo.

echo [3/4] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo [4/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
) else (
    echo .env file already exists, skipping...
)
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To activate the environment: venv\Scripts\activate
echo To run the agent: python -m src.main
echo To run tests: pytest tests -v
echo.
pause
