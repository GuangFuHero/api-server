#!/bin/bash
set -e

# === Config ===
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
FILENAME="${POSTGRES_DB}_${TIMESTAMP}.sql"
BACKUP_PATH="${BACKUP_DIR}/${FILENAME}"

echo "[$(date)] Starting PostgreSQL backup..."
export PGPASSWORD="${POSTGRES_PASSWORD}"
# === Dump Database ===
pg_dump -h postgres -U "${POSTGRES_USER}" "${POSTGRES_DB}" >"${BACKUP_PATH}"

# === Compress Backup ===
gzip "${BACKUP_PATH}"
echo "[$(date)] Backup created: ${FILENAME}.gz"

# === Keep Only 7 Most Recent Backups ===
cd "${BACKUP_DIR}"
BACKUP_COUNT=$(ls -1 *.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 7 ]; then
    echo "[$(date)] Found ${BACKUP_COUNT} backups. Removing older ones..."
    ls -1t *.gz | tail -n +8 | xargs rm -f
    echo "[$(date)] Old backups removed."
fi

echo "[$(date)] Backup finished successfully!"
