#!/usr/bin/env bash
# =============================================================================
# RedLink Hemovigilance System — Linux/macOS Quick Setup Script
# Usage: bash scripts/setup.sh
# =============================================================================
set -e

echo ""
echo "========================================"
echo "  RedLink – Hemovigilance System Setup  "
echo "========================================"
echo ""

# 1. Create virtual environment
if [ ! -d "venv" ]; then
    echo "[1/6] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/6] Virtual environment already exists. Skipping."
fi

# 2. Activate virtual environment
echo "[2/6] Activating virtual environment..."
source venv/bin/activate

# 3. Install dependencies
echo "[3/6] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy env file
if [ ! -f ".env" ]; then
    echo "[4/6] Creating .env from .env.example..."
    cp .env.example .env
    echo "      ⚠  Please update .env with your actual settings before running."
else
    echo "[4/6] .env already exists. Skipping."
fi

# 5. Run migrations
echo "[5/6] Running database migrations..."
python manage.py migrate

# 6. Collect static files
echo "[6/6] Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅  Setup complete!"
echo ""
echo "To start the development server:"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "To create a superuser:"
echo "    python manage.py createsuperuser"
echo ""
