#!/bin/bash
set -e

echo "=== VERCEL BUILD STARTED ==="

# Set VERCEL environment flags and bypass PEP 668 externally managed environment restriction
export VERCEL=1
export PIP_BREAK_SYSTEM_PACKAGES=1

echo "Installing project dependencies..."
if command -v uv &> /dev/null; then
    echo "Detected uv environment. Installing dependencies via uv..."
    uv pip install --system -r requirements.txt || python3 -m pip install --break-system-packages -r requirements.txt || true
elif python3 -m pip install --break-system-packages -r requirements.txt; then
    echo "Dependencies installed via pip (--break-system-packages)."
else
    echo "Falling back to virtual environment for build..."
    python3 -m venv .build_venv
    source .build_venv/bin/activate
    pip install -r requirements.txt
fi

echo "Collecting static assets..."
python3 manage.py collectstatic --noinput --clear

echo "=== VERCEL BUILD COMPLETED ==="
