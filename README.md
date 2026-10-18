#PAV.RENTAL — Odoo Community
Sistem informasi penyewaan motor PAV.RENTAL 

## Menjalankan di GitHub Codespaces
1. Code → Codespaces → Create codespace on staging
2. Di terminal: `docker compose up -d`
3. Buka tab Ports → 8069 → klik ikon bola dunia

## Struktur
- `addons/` : modul kustom Odoo (tim ERP)
- `.devcontainer/` : konfigurasi Codespaces
- `docker-compose.yml` : Odoo + PostgreSQL

## Alur kerja Git
`feature/<nama>` → Pull Request → `staging` → Pull Request → `main`
Jangan commit langsung ke `main` atau `staging`.
