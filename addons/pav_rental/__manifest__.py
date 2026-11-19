{
    "name": "PAV.RENTAL",
    "summary": "Penyewaan kendaraan PAV.RENTAL",
    "version": "19.0.1.2.0",
    "category": "Services",
    "author": "Kelompok Bikini Bottom - Telkom University",
    "depends": ["mail", "fleet", "contacts", "sale", "calendar", "account"],
    "data": [
        "security/ir.model.access.csv",
        "data/pav_rental_data.xml",
        "data/reservasi_sequence.xml",
        "views/armada_views.xml",
        "views/reservasi_views.xml",
        "views/menu.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
