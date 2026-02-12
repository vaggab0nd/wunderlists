#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
