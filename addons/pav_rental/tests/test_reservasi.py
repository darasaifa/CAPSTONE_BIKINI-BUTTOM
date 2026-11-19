from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestReservasi(TransactionCase):
    """Skenario uji black box dari proposal (Tahap 2), dijalankan otomatis oleh CI.

    Jadwal awal: NMAX sudah dipesan dan dikonfirmasi 21 s.d. 23 Nov 2026.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        honda = cls.env.ref('fleet.brand_honda')
        Kendaraan = cls.env['fleet.vehicle']

        def motor(nama, plat, harian, mingguan, **lain):
            return Kendaraan.create(dict({
                'rental_vehicle_name': nama,
                'rental_brand_id': honda.id,
                'license_plate': plat,
                'rental_tarif_harian': harian,
                'rental_tarif_mingguan': mingguan,
            }, **lain))

        cls.nmax = motor('NMAX Uji', 'KT 9911 UJI', 150000, 900000)
        cls.genio = motor('Genio Uji', 'KT 9912 UJI', 110000, 660000)
        cls.beat = motor('Beat Uji', 'KT 9913 UJI', 85000, 510000, rental_minimal_hari=2)
        cls.aerox = motor('Aerox Uji', 'KT 9914 UJI', 150000, 900000, rental_status='service')
        cls.pelanggan = cls.env['res.partner'].create({'name': 'Pelanggan Uji'})
        cls.Reservasi = cls.env['pav.rental.reservasi']

        cls.lama = cls._reservasi(cls.nmax, '2026-11-21', '2026-11-23')
        cls.lama.action_konfirmasi()

    @classmethod
    def _reservasi(cls, motor, mulai, selesai, **lain):
        return cls.Reservasi.create(dict({
            'partner_id': cls.pelanggan.id,
            'vehicle_id': motor.id,
            'tanggal_mulai': mulai,
            'tanggal_selesai': selesai,
        }, **lain))

    # --- Pencegahan double booking ---
    def test_bentrok_penuh_ditolak(self):
        baru = self._reservasi(self.nmax, '2026-11-21', '2026-11-23')
        with self.assertRaises(ValidationError):
            baru.action_konfirmasi()

    def test_bentrok_sebagian_ditolak(self):
        baru = self._reservasi(self.nmax, '2026-11-22', '2026-11-24')
        with self.assertRaises(ValidationError):
            baru.action_konfirmasi()

    def test_tepat_setelah_sewa_lain_selesai_diterima(self):
        baru = self._reservasi(self.nmax, '2026-11-23', '2026-11-25')
        baru.action_konfirmasi()
        self.assertEqual(baru.state, 'confirmed')

    def test_draf_boleh_tumpang_tindih_sebelum_dikonfirmasi(self):
        draf = self._reservasi(self.nmax, '2026-11-22', '2026-11-24')
        self.assertEqual(draf.state, 'draft')

    def test_reservasi_batal_tidak_menghalangi(self):
        self.lama.action_batal()
        baru = self._reservasi(self.nmax, '2026-11-21', '2026-11-23')
        baru.action_konfirmasi()
        self.assertEqual(baru.state, 'confirmed')

    # --- Ketersediaan motor dan aturan sewa ---
    def test_motor_servis_ditolak(self):
        baru = self._reservasi(self.aerox, '2026-11-23', '2026-11-25')
        with self.assertRaises(ValidationError):
            baru.action_konfirmasi()

    def test_beat_kurang_dari_minimal_dua_hari_ditolak(self):
        baru = self._reservasi(self.beat, '2026-11-23', '2026-11-24')
        with self.assertRaises(ValidationError):
            baru.action_konfirmasi()

    def test_tanggal_selesai_sebelum_mulai_ditolak(self):
        with self.assertRaises(ValidationError):
            self._reservasi(self.genio, '2026-11-25', '2026-11-23')

    # --- Perhitungan tarif ---
    def test_matic_satu_hari_rp110000(self):
        baru = self._reservasi(self.genio, '2026-11-20', '2026-11-21')
        self.assertEqual(baru.jumlah_hari, 1)
        self.assertEqual(baru.total, 110000)

    def test_paket_mingguan_memakai_tarif_mingguan(self):
        baru = self._reservasi(self.genio, '2026-11-23', '2026-11-30', paket='mingguan')
        self.assertEqual(baru.total, 660000)

    def test_biaya_antar_jemput_ditambahkan(self):
        baru = self._reservasi(self.genio, '2026-11-20', '2026-11-22',
                               antar_jemput=True, biaya_antar=25000)
        self.assertEqual(baru.total, 2 * 110000 + 25000)

    def test_tarif_lama_tidak_berubah_saat_tarif_motor_naik(self):
        baru = self._reservasi(self.genio, '2026-11-20', '2026-11-21')
        self.genio.rental_tarif_harian = 120000
        self.assertEqual(baru.total, 110000)

    # --- Alur status ---
    def test_nomor_otomatis(self):
        self.assertTrue(self.lama.name.startswith('RSV/'))

    def test_serah_terima_dan_kembali_mengubah_status_motor(self):
        self.lama.action_mulai_sewa()
        self.assertEqual(self.nmax.rental_status, 'rented')
        self.lama.action_selesai()
        self.assertEqual(self.lama.state, 'done')
        self.assertEqual(self.nmax.rental_status, 'available')
