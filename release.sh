#!/bin/bash
# Exit script in case an error occurs.
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Add other necessary release tasks here.
