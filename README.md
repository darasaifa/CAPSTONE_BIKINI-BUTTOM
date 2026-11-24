## Cara jalanin

Pastikan Git dan Docker Desktop udah terpasang, terus:

```
git clone https://github.com/darasaifa/CAPSTONE_BIKINI-BUTTOM.git
cd CAPSTONE_BIKINI-BUTTOM
copy .env.example .env
docker compose up -d
```

Buka http://localhost:8069, bikin database `pavrental`, pilih bahasa Indonesia, jangan centang demo data. Master password-nya dicatat!

Matiin: `docker compose stop`
Abis ubah kode Python: `docker compose restart odoo`

Jangan pakai `docker compose down -v`, database nanti bakal kehapus.

## Alur kerja

Jangan push langsung ke `main` atau `staging`. Bikin branch dari `staging` dulu:

```
git checkout staging
git pull
git checkout -b nama/fitur
```

Kalau udah, push branch-nya terus bikin Pull Request ke `staging`.

Modul kustom taruh di folder `addons`.