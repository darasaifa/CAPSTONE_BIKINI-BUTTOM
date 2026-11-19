from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestArmada(TransactionCase):
    """Tes otomatis untuk data armada (models/armada.py).

    Dijalankan CI di setiap Pull Request. Contoh pola tes untuk modul lain,
    misalnya tests/test_reservasi.py untuk validasi double booking.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.honda = cls.env.ref('fleet.brand_honda')
        cls.Kendaraan = cls.env['fleet.vehicle']

    def _buat_motor(self, nama, plat):
        return self.Kendaraan.create({
            'rental_vehicle_name': nama,
            'rental_brand_id': self.honda.id,
            'license_plate': plat,
        })

    def test_model_fleet_dibuat_otomatis_dari_nama_dan_merek(self):
        motor = self._buat_motor('Vario Uji CI', 'KT 9901 UJI')
        self.assertEqual(motor.model_id.name, 'Vario Uji CI')
        self.assertEqual(motor.model_id.brand_id, self.honda)

    def test_nama_dan_merek_sama_memakai_model_yang_sama(self):
        motor_1 = self._buat_motor('Beat Uji CI', 'KT 9902 UJI')
        motor_2 = self._buat_motor('Beat Uji CI', 'KT 9903 UJI')
        self.assertEqual(motor_1.model_id, motor_2.model_id)

    def test_ganti_nama_ikut_mengganti_model(self):
        motor = self._buat_motor('Genio Uji CI', 'KT 9904 UJI')
        motor.write({'rental_vehicle_name': 'Genio Baru Uji CI'})
        self.assertEqual(motor.model_id.name, 'Genio Baru Uji CI')

    def test_status_awal_tersedia(self):
        motor = self._buat_motor('Scoopy Uji CI', 'KT 9905 UJI')
        self.assertEqual(motor.rental_status, 'available')
