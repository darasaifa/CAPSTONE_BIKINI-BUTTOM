{
    "name": "PAV.RENTAL - Data Contoh",
    "summary": "Data contoh fiktif agar database pengembangan semua anggota sama. "
               "Jangan dipasang di production.",
    "description": """
Data contoh fiktif untuk pengembangan dan staging PAV.RENTAL.

Semua nama, nomor polisi, dan nomor telepon di modul ini dikarang
(berakhiran CTH / diberi label "Contoh"), bukan data asli mitra,
sesuai prinsip pembatasan data pada UU PDP.
Modul ini TIDAK boleh dipasang di production.
""",
    "version": "19.0.1.1.0",
    "category": "Services",
    "author": "Kelompok Bikini Bottom - Telkom University",
    "depends": ["pav_rental"],
    "data": [
        "data/armada_contoh.xml",
        "data/tarif_contoh.xml",
        "data/pelanggan_contoh.xml",
        "data/reservasi_contoh.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
