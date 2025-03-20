#!/bin/bash
# entrypoint.sh

# Wait for a few seconds to ensure services are ready
sleep 10

# Run migrations
python manage.py flush --no-input
python manage.py migrate

# Seed the database
echo "Starting database seeding"
python manage.py seed

# Start the application
exec gunicorn --bind 0.0.0.0:8000 project.wsgi:application
