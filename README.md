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

## Backup dan restore

Backup database + filestore, hasilnya masuk folder `backups`:

```
docker compose run --rm backup /scripts/backup.sh
```

Coba restore ke database baru, aman karena database asli gak disentuh:

```
docker compose run --rm backup /scripts/restore.sh nama_file_backup.tar.gz pavrental_uji
```

Mau restore ke database yang udah ada? Matiin Odoo dulu, terus tambah `-e TIMPA=ya`:

```
docker compose stop odoo
docker compose run --rm -e TIMPA=ya backup /scripts/restore.sh nama_file_backup.tar.gz
docker compose start odoo
```

Folder `backups` gak ikut ke GitHub karena isinya data asli.

## Production

Ini buat di server, bukan di laptop. Bedanya: halaman pengelola database ditutup, port gak dibuka ke luar (akses lewat Cloudflare Tunnel), dan Odoo jalan pakai beberapa proses.

Siapin dulu dua file rahasia, dua-duanya gak ikut ke GitHub:

```
cp .env.example .env
cp config/odoo.conf.example config/odoo.conf
```

Isi `.env` pakai password database yang kuat plus token Cloudflare, terus ganti `admin_passwd` di `config/odoo.conf`.

Data awal diambil dari file backup, taruh di folder `backups`:

```
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d db
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm backup /scripts/restore.sh nama_file_backup.tar.gz
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile tunnel up -d
```

## Alur kerja

Jangan push langsung ke `main` atau `staging`. Bikin branch dari `staging` dulu:

```
git checkout staging
git pull
git checkout -b nama/fitur
```

Kalau udah, push branch-nya terus bikin Pull Request ke `staging`.

Modul kustom taruh di folder `addons`.