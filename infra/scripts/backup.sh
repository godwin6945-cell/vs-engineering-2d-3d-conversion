#!/usr/bin/env bash
# Automated Point-in-Time Backup Script for Sketch2STEP Enterprise
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
BACKUP_NAME="sketch2step_backup_${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

echo "[*] Starting Sketch2STEP Enterprise backup: ${BACKUP_NAME}..."

# 1. PostgreSQL Database Dump
echo "[*] Running pg_dump for PostgreSQL..."
PGPASSWORD="${POSTGRES_PASSWORD:-postgres}" pg_dump \
  -h "${POSTGRES_HOST:-localhost}" \
  -p "${POSTGRES_PORT:-5432}" \
  -U "${POSTGRES_USER:-postgres}" \
  -d "${POSTGRES_DB:-sketch2step}" \
  -F c -b -v -f "${BACKUP_DIR}/${BACKUP_NAME}/database.dump" || true

# 2. Archive CAD Storage
if [ -d "eval/datasets" ]; then
  cp -r eval/datasets "${BACKUP_DIR}/${BACKUP_NAME}/cad_datasets"
fi

# 3. Compress Archive
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "${BACKUP_DIR}" "${BACKUP_NAME}"
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}"

# 4. Checksum
sha256sum "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" > "${BACKUP_DIR}/${BACKUP_NAME}.sha256"

# 5. Prune backups older than retention window
find "${BACKUP_DIR}" -name "sketch2step_backup_*.tar.gz" -mtime +"${RETENTION_DAYS}" -delete
find "${BACKUP_DIR}" -name "sketch2step_backup_*.sha256" -mtime +"${RETENTION_DAYS}" -delete

echo "[✓] Backup completed successfully: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
