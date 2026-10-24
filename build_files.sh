#!/bin/bash
set -e

echo "=== VERCEL BUILD STARTED ==="

# Set VERCEL environment flag
export VERCEL=1

echo "Installing project dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static assets..."
python3 manage.py collectstatic --noinput --clear

echo "Applying migrations if database is accessible..."
python3 manage.py migrate --noinput || true

echo "=== VERCEL BUILD COMPLETED ==="
