#!/usr/bin/env bash
# Backup database dan filestore Odoo jadi satu file di folder backups/.
# Pakai: docker compose run --rm backup /scripts/backup.sh [nama_database]
set -euo pipefail

DB="${1:-${DB_NAME:-pavrental}}"
WAKTU="$(date +%Y%m%d-%H%M%S)"
KERJA="$(mktemp -d)"
trap 'rm -rf "$KERJA"' EXIT

echo "Backup database $DB ..."
pg_dump --format=custom --no-owner --file="$KERJA/database.dump" "$DB"

if [ -d "/var/lib/odoo/filestore/$DB" ]; then
  echo "Backup filestore $DB ..."
  tar -C /var/lib/odoo/filestore -czf "$KERJA/filestore.tar.gz" "$DB"
else
  echo "Filestore $DB belum ada, dilewati."
fi

printf 'db=%s\nwaktu=%s\n' "$DB" "$WAKTU" > "$KERJA/info.txt"

HASIL="/backups/${DB}_${WAKTU}.tar.gz"
tar -C "$KERJA" -czf "$HASIL" .
echo "Selesai: backups/$(basename "$HASIL") ($(du -h "$HASIL" | cut -f1))"

# Hapus backup yang lebih tua dari SIMPAN_HARI hari.
find /backups -maxdepth 1 -name "${DB}_*.tar.gz" -mtime +"${SIMPAN_HARI:-14}" -print -delete \
  | sed 's|^/backups/|Dihapus karena sudah lama: |'
