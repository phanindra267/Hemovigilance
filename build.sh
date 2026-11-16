#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static assets..."
python manage.py collectstatic --no-input

echo "Applying database schema migrations..."
python manage.py migrate

echo "Seeding default demo data..."
python manage.py seed_demo_data

echo "Build and preparation completed successfully!"
