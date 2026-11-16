@echo off
REM =============================================================================
REM  RedLink Hemovigilance System — Windows Quick Setup Script
REM  Usage: scripts\setup.bat
REM =============================================================================

echo.
echo ========================================
echo   RedLink - Hemovigilance System Setup
echo ========================================
echo.

REM 1. Create virtual environment
IF NOT EXIST "venv\" (
    echo [1/6] Creating virtual environment...
    python -m venv venv
) ELSE (
    echo [1/6] Virtual environment already exists. Skipping.
)

REM 2. Activate virtual environment
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

REM 3. Install dependencies
echo [3/6] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 4. Copy env file
IF NOT EXIST ".env" (
    echo [4/6] Creating .env from .env.example...
    copy .env.example .env
    echo       WARNING: Please update .env with your actual settings before running.
) ELSE (
    echo [4/6] .env already exists. Skipping.
)

REM 5. Run migrations
echo [5/6] Running database migrations...
python manage.py migrate

REM 6. Collect static files
echo [6/6] Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Setup complete!
echo.
echo To start the development server:
echo     venv\Scripts\activate.bat
echo     python manage.py runserver
echo.
echo To create a superuser:
echo     python manage.py createsuperuser
echo.
pause
