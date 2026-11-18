# PAV.RENTAL (Odoo 19 Community)

## Teknologi
| Komponen | Versi |
|---|---|
| Odoo Community | 19.0 (jangan 20) |
| PostgreSQL | 16 |
| Lingkungan kerja | Odoo 19 di laptop Windows + VS Code |

## Struktur repo
```
addons/pav_rental/                modul utama PAV.RENTAL
addons/pav_rental/tests/          tes otomatis modul (dijalankan CI)
addons/pav_rental_demo/           data contoh FIKTIF untuk laptop dan staging (bukan production)
scripts/sambung-odoo-lokal.ps1    menyambungkan addons repo ke Odoo 19 di Windows
.github/workflows/ci.yml          pemeriksaan otomatis setiap push dan Pull Request
.gitignore                        berkas yang tidak boleh masuk Git
```
Direncanakan (belum dibuat), untuk server staging dan production: `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `config/odoo.conf`, `config/odoo.prod.conf`, deploy otomatis ke server (CD).

Setiap modul harus berada tepat satu tingkat di bawah `addons/`, contoh: `addons/nama_modul/__manifest__.py`.

## Memulai: Odoo 19 di laptop Windows (sekali per anggota)
1. Pasang **VS Code** (`https://code.visualstudio.com`) dan **Git for Windows** (`https://git-scm.com/download/win`, semua pilihan bawaan).
2. Unduh installer **Odoo 19** Community untuk Windows:
   `https://nightly.odoo.com/19.0/nightly/windows/odoo_19.0.latest.exe`
3. Klik kanan installer → **Run as administrator**. Centang **Odoo Server** dan **PostgreSQL Database**. Folder tujuan boleh di D:.
4. Kenalkan diri ke Git (sekali saja). Di VS Code buka terminal (`` Ctrl+` ``), lalu jalankan:
   ```powershell
   git config --global user.name "Nama Lengkap"
   git config --global user.email "email-akun-github-kamu"
   ```
   Pakai email yang sama dengan akun GitHub supaya commit tercatat sebagai kontribusimu.
5. Clone repo di VS Code: `Ctrl+Shift+P` → **Git: Clone** → tempel URL repo → pilih folder `D:\Project`. Kalau diminta masuk ke GitHub, izinkan.
6. Buka PowerShell **sebagai administrator**, lalu jalankan:
   ```powershell
   cd D:\Project\CAPSTONE_BIKINI-BUTTOM
   powershell -ExecutionPolicy Bypass -File .\scripts\sambung-odoo-lokal.ps1
   ```
7. Buka `http://localhost:8069` dan buat database:
   - Database Name: `pavrental_dev`
   - Country: Indonesia
   - Demo data: **jangan dicentang**
   - Simpan Master Password dan kata sandi login di tempat aman.
8. Nyalakan Developer Mode: buka `http://localhost:8069/odoo?debug=1`.
9. **Apps** → **Update Apps List** → cari `PAV` → **Activate** **PAV.RENTAL**, lalu **Activate** **PAV.RENTAL - Data Contoh**.

Kalau Odoo terbuka tetapi database tidak bisa dibuat (log berisi `Connection to the database failed`), PostgreSQL gagal terpasang. Penyebab yang pernah terjadi: unduhan PostgreSQL dari installer Odoo terputus, atau Smart App Control Windows memblokir file PostgreSQL. Hubungi EIM.

## Agar database semua anggota sejalan
Git tidak menyimpan database. Yang dibagikan lewat repo adalah **kode modul dan berkas data**. Setiap anggota punya database `pavrental_dev` sendiri, lalu isinya disamakan dengan memasang modul yang sama.

| Lewat Git (sama untuk semua) | Tidak lewat Git (hanya di laptop sendiri) |
|---|---|
| Model, tampilan, aturan validasi (`addons/pav_rental`) | Data yang diketik langsung di Odoo |
| Data dasar yang dibutuhkan semua lingkungan (`addons/pav_rental/data/`) | Kata sandi, Master Password, `odoo.conf` |
| Data contoh fiktif (`addons/pav_rental_demo/data/`) | Cadangan database (`.dump`, `.zip`, `.sql`) |

Setiap selesai `git pull`:
1. Kalau ada file `.py` yang berubah, restart Odoo dulu:
   `powershell -ExecutionPolicy Bypass -File .\scripts\sambung-odoo-lokal.ps1 -RestartSaja` (sebagai administrator).
2. Di Odoo: **Apps** → cari `PAV` → pada kartu **PAV.RENTAL** klik **⋮** → **Upgrade**. Lakukan juga untuk **PAV.RENTAL - Data Contoh** kalau berkas datanya berubah.

Data yang harus dimiliki semua anggota jangan hanya diketik di Odoo. Jadikan berkas XML atau CSV:
- data yang juga dipakai di production (misalnya merek, kategori, grup hak akses) → `addons/pav_rental/data/`
- data contoh fiktif untuk mencoba dan demo → `addons/pav_rental_demo/data/`

Database yang benar-benar satu untuk semua orang adalah **staging** di server dosen. 

## Alur kerja Git
```
<Nama>/<tugas>  →  Pull Request  →  staging  →  Pull Request  →  main
```
| Branch | Fungsi |
|---|---|
| `main` | Versi stabil, hanya diisi setelah demo disetujui. |
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
Lalu ajukan Pull Request ke `staging` dan minta satu anggota lain meninjaunya. Hapus branch setelah di-merge, lalu buat branch baru untuk tugas berikutnya.

Catatan penamaan: jangan membuat branch yang hanya bernama `Nama` (misalnya `Dara`), karena bentrok dengan `Dara/tugas` dan ditolak Git.

## Pemeriksaan otomatis (CI)
Setiap kali kamu push atau membuat Pull Request ke `staging`/`main`, GitHub otomatis:
1. menyalakan Odoo 19 dan PostgreSQL 16 versi Docker (sama dengan rencana server),
2. memasang **PAV.RENTAL** dan **PAV.RENTAL - Data Contoh** ke database kosong,
3. menjalankan semua tes di folder `tests/` modul tersebut.

Hasilnya muncul di halaman Pull Request: **centang hijau** berarti lolos, **silang merah** berarti ada yang rusak. Klik **Details** untuk membaca log. Butuh sekitar 5–10 menit.

Menambah tes untuk fitur baru: buat berkas `tests/test_<fitur>.py` di modulnya, lalu daftarkan di `tests/__init__.py`. Contohnya ada di `addons/pav_rental/tests/test_armada.py`.

## Aturan tim
- Jangan commit langsung ke `main` atau `staging`.
- Pull Request hanya boleh di-merge kalau CI centang hijau dan sudah ditinjau satu anggota lain.
- Jangan commit kata sandi, berkas `.env`, `odoo.conf`, atau cadangan database.
- Data contoh wajib fiktif. Jangan memasukkan data pelanggan asli mitra ke repo (UU PDP).
- Kode final wajib masuk lewat repo (branch → Pull Request).
- Versi dikunci: Odoo 19.0 dan PostgreSQL 16.

## Perintah berguna
| Tujuan | Perintah / langkah |
|---|---|
| Sambungkan repo ke Odoo | `scripts\sambung-odoo-lokal.ps1` (administrator) |
| Restart Odoo setelah ubah `.py` | `scripts\sambung-odoo-lokal.ps1 -RestartSaja` (administrator) |
| Terapkan perubahan XML/data | Apps → PAV.RENTAL → **⋮** → **Upgrade** |
| Lihat log Odoo | `<folder Odoo 19>\server\odoo.log` |

## Tim
| Peran | Anggota |
|---|---|
| EIM (infrastruktur dan keamanan) | Dara Saifa Mahiroh |
| ERP | Syifa Rizani, Farisha Huwaida Shofha |
