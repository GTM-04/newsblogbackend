#!/bin/bash

# Railway startup script for Django

echo "Starting Django application..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start Gunicorn
echo "Starting Gunicorn server on port ${PORT:-8080}..."
gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8080} --workers 3 --timeout 120
