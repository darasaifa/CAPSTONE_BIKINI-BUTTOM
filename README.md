# PAV.RENTAL (Odoo 19 Community)

Sistem informasi penyewaan motor PAV.RENTAL.
Capstone Design Project, S1 Sistem Informasi, Telkom University.

## Teknologi
| Komponen | Versi |
|---|---|
| Odoo Community | 19.0 |
| PostgreSQL | 16 |
| Lingkungan kerja | GitHub Codespaces (Ubuntu 24.04 + Docker) |

## Struktur repo
```
.devcontainer/devcontainer.json   resep Codespace (Ubuntu 24.04 + Docker)
addons/                           modul kustom Odoo buatan tim ERP
config/odoo.conf                  konfigurasi Odoo untuk pengembangan
config/odoo.prod.conf             template konfigurasi untuk server (tanpa kata sandi asli)
Dockerfile                        image Odoo proyek (Odoo 19 + library tambahan)
requirements.txt                  library Python tambahan untuk modul kustom
docker-compose.yml                menjalankan Odoo + PostgreSQL
.gitignore                        berkas yang tidak boleh masuk Git
```
Setiap modul harus berada tepat satu tingkat di bawah `addons/`, contoh: `addons/nama_modul/__manifest__.py`.

## Memulai (sekali per anggota)
1. Terima undangan collaborator dari GitHub.
2. Klik **Code → Codespaces → Create codespace on staging**. Tunggu 3-5 menit.
3. Cek di terminal: `docker compose ps` (db dan odoo harus Up).
4. Tab **Ports (Harbor)** → port **8069** → klik ikon bola dunia. Biarkan visibilitas **Private**.
5. Buat database `pavrental_dev` tanpa demo data, lalu pasang modul: Sales, Fleet, Contacts, Calendar, Invoicing.

## Alur kerja Git
```
<Nama>/<tugas>  →  Pull Request  →  staging  →  Pull Request  →  main
```
| Branch | Fungsi |
|---|---|
| `main` | Versi stabil, hanya diisi setelah demo disetujui. Dirilis oleh EIM. |
| `staging` | Gabungan hasil kerja yang sudah diperiksa, untuk uji dan demo. |
| `<Nama>/<tugas>` | Tempat kerja harian. Satu tugas, satu branch. |

Contoh nama branch:
- `Dara/dockerfile-config`
- `Syifa/sale-calendar`
- `Farisha/fleet-modifikasi`

Setiap mengerjakan tugas:
```bash
git checkout staging
git pull
git checkout -b Nama/nama-tugas
# ... kerjakan, lalu:
git add -A
git commit -m "Pesan singkat tentang perubahan"
git push -u origin Nama/nama-tugas
```
Lalu ajukan Pull Request ke `staging`. Hapus branch setelah di-merge, lalu buat branch baru untuk tugas berikutnya.

Catatan penamaan: jangan membuat branch yang hanya bernama `Nama` (misalnya `Dara`), karena bentrok dengan `Dara/tugas` dan ditolak Git.

## Aturan tim
- Jangan commit langsung ke `main` atau `staging`.
- Perubahan pada `.devcontainer/`, `docker-compose.yml`, `Dockerfile`, atau `config/` wajib diperiksa EIM.
- Jangan commit kata sandi atau berkas `.env`. Isi `admin_passwd` di `config/odoo.prod.conf` hanya placeholder.
- Data yang diketik di Odoo tersimpan di database Codespace masing-masing, bukan di Git. Pengaturan yang harus sama untuk semua anggota dibuat sebagai berkas data XML atau CSV di dalam modul.
- Odoo di laptop hanya untuk mencoba. Kode final wajib masuk lewat repo.
- Hentikan Codespace setelah selesai bekerja: github.com/codespaces → **⋯** → **Stop codespace**.
- Versi dikunci: Odoo 19.0 dan PostgreSQL 16.

## Perintah berguna
| Tujuan | Perintah |
|---|---|
| Cek container | `docker compose ps` |
| Jalankan ulang setelah mengubah Dockerfile | `docker compose up -d --build` |
| Restart Odoo setelah ubah kode | `docker compose restart odoo` |
| Lihat log Odoo | `docker compose logs -f odoo` |
| Matikan Odoo (data aman) | `docker compose down` (jangan pakai `-v`) |
| Bangun ulang Codespace | Ctrl+Shift+P → Codespaces: Rebuild Container |

## Tim
| Peran | Anggota |
|---|---|
| EIM (infrastruktur dan keamanan) | Dara Saifa Mahiroh |
| ERP | Syifa Rizani, Farisha Huwaida Shofha |