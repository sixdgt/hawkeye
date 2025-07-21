#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL is up - continuing..."

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files (optional)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Run the command passed to the container
exec "$@"
