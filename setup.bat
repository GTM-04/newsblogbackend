@echo off
echo ========================================
echo Pulse ^& Passion Backend Setup
echo ========================================
echo.

echo [1/6] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo [4/6] Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please update it with your database credentials.
) else (
    echo .env file already exists. Skipping...
)

echo [5/6] Running migrations...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error: Failed to run migrations. Make sure PostgreSQL is running and configured.
    exit /b 1
)

echo [6/6] Creating media directories...
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update .env file with your database credentials
echo 2. Create a superuser: python manage.py createsuperuser
echo 3. Run the server: python manage.py runserver
echo 4. Access admin at: http://localhost:8000/admin/
echo 5. Access API at: http://localhost:8000/api/
echo.
pause
