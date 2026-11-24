#!/usr/bin/env bash
# Kembalikan backup ke database Odoo.
# Pakai: docker compose run --rm backup /scripts/restore.sh <file_backup> [nama_database_tujuan]
# Tanpa nama tujuan, backup dikembalikan ke database aslinya.
# Kalau database tujuan sudah ada, tambahkan -e TIMPA=ya dan matikan Odoo dulu.
set -euo pipefail

FILE="${1:?Pakai: restore.sh <file_backup> [nama_database_tujuan]}"
case "$FILE" in
  /*) ;;
  *) FILE="/backups/$(basename "$FILE")" ;;
esac
[ -f "$FILE" ] || { echo "File $FILE tidak ditemukan. Lihat isi folder backups."; exit 1; }

MULAI=$(date +%s)
KERJA="$(mktemp -d)"
trap 'rm -rf "$KERJA"' EXIT
tar -C "$KERJA" -xzf "$FILE"

ASAL="$(sed -n 's/^db=//p' "$KERJA/info.txt")"
TUJUAN="${2:-$ASAL}"
case "$TUJUAN" in
  *[!a-zA-Z0-9_-]*|"") echo "Nama database hanya boleh huruf, angka, - dan _."; exit 1 ;;
esac

ADA="$(psql -d postgres -Atc "SELECT 1 FROM pg_database WHERE datname = '$TUJUAN'")"
if [ "$ADA" = "1" ]; then
  if [ "${TIMPA:-}" != "ya" ]; then
    echo "Database $TUJUAN sudah ada, restore dibatalkan."
    echo "Untuk menimpanya: matikan Odoo (docker compose stop odoo), lalu jalankan ulang dengan -e TIMPA=ya."
    exit 1
  fi
  echo "Menghapus database $TUJUAN yang lama ..."
  dropdb "$TUJUAN" 2>/dev/null || {
    echo "Gagal menghapus $TUJUAN karena masih dipakai Odoo."
    echo "Jalankan docker compose stop odoo dulu, lalu ulangi."
    exit 1
  }
fi

echo "Mengembalikan database $ASAL ke $TUJUAN ..."
createdb "$TUJUAN"
pg_restore --no-owner --dbname="$TUJUAN" "$KERJA/database.dump"

if [ -f "$KERJA/filestore.tar.gz" ]; then
  echo "Mengembalikan filestore ..."
  mkdir -p /var/lib/odoo/filestore "$KERJA/fs"
  tar -C "$KERJA/fs" -xzf "$KERJA/filestore.tar.gz"
  rm -rf "/var/lib/odoo/filestore/$TUJUAN"
  mv "$KERJA/fs/$ASAL" "/var/lib/odoo/filestore/$TUJUAN"
fi

# Folder data harus milik pengguna Odoo (100:101 di image resmi Odoo).
# Penting di server baru, saat restore dijalankan sebelum Odoo pernah menyala.
PEMILIK="${ODOO_UID:-100}:${ODOO_GID:-101}"
mkdir -p /var/lib/odoo/filestore
chown "$PEMILIK" /var/lib/odoo /var/lib/odoo/filestore
[ -d "/var/lib/odoo/filestore/$TUJUAN" ] && chown -R "$PEMILIK" "/var/lib/odoo/filestore/$TUJUAN"

echo "Selesai dalam $(( $(date +%s) - MULAI )) detik. Database: $TUJUAN"
