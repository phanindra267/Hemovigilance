#!/usr/bin/env bash
# =============================================================================
# RedLink Hemovigilance System — Seed Demo Data Script
# Usage: bash scripts/seed_data.sh
# =============================================================================
set -e

echo ""
echo "========================================"
echo "  RedLink – Seeding Demo Data           "
echo "========================================"
echo ""

# Activate venv if present
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "⏳  Running seed management command..."
python manage.py seed_demo_data

echo ""
echo "✅  Demo data seeded successfully!"
echo "    You can now log in with the demo accounts described in README.md"
echo ""
