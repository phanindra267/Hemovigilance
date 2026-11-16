#!/usr/bin/env bash
# =============================================================================
# RedLink Hemovigilance System — PostgreSQL Database Backup Script
# Usage: bash scripts/backup_db.sh
# =============================================================================
set -e

# ---------------------------------------------------------------------------
# Configuration — override via environment variables or .env
# ---------------------------------------------------------------------------
source .env 2>/dev/null || true

DB_NAME="${DB_NAME:-redlink_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/redlink_backup_${TIMESTAMP}.sql.gz"

# ---------------------------------------------------------------------------
# Run backup
# ---------------------------------------------------------------------------
mkdir -p "$BACKUP_DIR"

echo "⏳  Backing up database '${DB_NAME}' → ${BACKUP_FILE}"

PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "✅  Backup complete: ${BACKUP_FILE}"

# ---------------------------------------------------------------------------
# Rotate: keep only the 10 most recent backups
# ---------------------------------------------------------------------------
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    echo "🔄  Rotating old backups (keeping 10 most recent)..."
    ls -1t "${BACKUP_DIR}"/*.sql.gz | tail -n +11 | xargs rm -f
fi

echo "📂  Backups in '${BACKUP_DIR}':"
ls -lh "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | awk '{print "   ", $9, $5}'
