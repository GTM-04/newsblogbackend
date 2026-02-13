#!/bin/bash

echo "========================================"
echo "Pulse & Passion Backend Setup"
echo "========================================"
echo ""

echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[4/6] Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update it with your database credentials."
else
    echo ".env file already exists. Skipping..."
fi

echo "[5/6] Running migrations..."
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: Failed to run migrations. Make sure PostgreSQL is running and configured."
    exit 1
fi

echo "[6/6] Creating media directories..."
mkdir -p media
mkdir -p staticfiles

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Create a superuser: python manage.py createsuperuser"
echo "3. Run the server: python manage.py runserver"
echo "4. Access admin at: http://localhost:8000/admin/"
echo "5. Access API at: http://localhost:8000/api/"
echo ""
