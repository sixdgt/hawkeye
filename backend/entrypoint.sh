#!/bin/bash

# Wait for PostgreSQL to be ready
until nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
  sleep 2
done

echo "PostgreSQL is up - executing command"

# Run migrations
python manage.py migrate

# Execute the command passed to the entrypoint (e.g., runserver)
exec "$@"