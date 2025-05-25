#!/bin/bash

echo "Waiting database..."
while ! nc -z database 5432; do
  sleep 0.1
done
echo "Database UP"

# Exec migrations
python manage.py migrate

# Run Server
exec python manage.py runserver 0.0.0.0:8000
