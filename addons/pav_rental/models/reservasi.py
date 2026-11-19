import math
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# Status yang "memakai" motor. Reservasi berstatus ini tidak boleh bentrok jadwal.
STATUS_AKTIF = ('confirmed', 'ongoing')


class Reservasi(models.Model):
    """Reservasi sewa motor PAV.RENTAL.

    Aturan jadwal: tanggal_mulai = hari motor diambil, tanggal_selesai = hari motor
    kembali. Sewa 21 s.d. 23 Nov dihitung 2 hari, dan motor yang sama boleh
    disewa lagi mulai 23 Nov.
    """

    _name = 'pav.rental.reservasi'
    _description = 'Reservasi Sewa Motor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tanggal_mulai desc, id desc'

    name = fields.Char(
        string='Nomor', default='Baru', required=True, readonly=True, copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner', string='Pelanggan', required=True, tracking=True,
    )
    vehicle_id = fields.Many2one(
        'fleet.vehicle', string='Motor', required=True, tracking=True,
    )
    tanggal_mulai = fields.Date(string='Mulai', required=True, tracking=True)
    tanggal_selesai = fields.Date(string='Selesai', required=True, tracking=True)
    jumlah_hari = fields.Integer(
        string='Durasi (hari)', compute='_compute_jumlah_hari', store=True,
    )
    paket = fields.Selection(
        [('harian', 'Harian'), ('mingguan', 'Mingguan')],
        string='Paket', default='harian', required=True,
    )

    currency_id = fields.Many2one(
        'res.currency', string='Mata Uang', required=True,
        default=lambda self: self.env.company.currency_id,
    )
    # Tarif disalin dari data motor saat motor/paket dipilih, supaya reservasi lama
    # tidak ikut berubah kalau tarif motor dinaikkan nanti.
    tarif = fields.Monetary(
        string='Tarif per Paket', compute='_compute_tarif', store=True, readonly=False,
    )
    biaya_sewa = fields.Monetary(string='Biaya Sewa', compute='_compute_biaya', store=True)
    antar_jemput = fields.Boolean(string='Antar-jemput')
    biaya_antar = fields.Monetary(string='Biaya Antar-jemput')
    total = fields.Monetary(string='Total', compute='_compute_biaya', store=True, tracking=True)

    state = fields.Selection(
        [
            ('draft', 'Draf'),
            ('confirmed', 'Dikonfirmasi'),
            ('ongoing', 'Disewa'),
            ('done', 'Selesai'),
            ('cancel', 'Batal'),
        ],
        string='Status', default='draft', required=True, tracking=True, copy=False,
    )
    catatan = fields.Text(string='Catatan')

    # ------------------------------------------------------------------
    # Hitungan otomatis
    # ------------------------------------------------------------------
    @api.depends('tanggal_mulai', 'tanggal_selesai')
    def _compute_jumlah_hari(self):
        for rec in self:
            if rec.tanggal_mulai and rec.tanggal_selesai:
                rec.jumlah_hari = (rec.tanggal_selesai - rec.tanggal_mulai).days
            else:
                rec.jumlah_hari = 0

    @api.depends('vehicle_id', 'paket')
    def _compute_tarif(self):
        for rec in self:
            if rec.paket == 'mingguan':
                rec.tarif = rec.vehicle_id.rental_tarif_mingguan
            else:
                rec.tarif = rec.vehicle_id.rental_tarif_harian

    @api.depends('jumlah_hari', 'paket', 'tarif', 'antar_jemput', 'biaya_antar')
    def _compute_biaya(self):
        for rec in self:
            hari = max(rec.jumlah_hari, 0)
            if rec.paket == 'mingguan':
                # TODO Farisha: pastikan ke mitra, sewa 10 hari paket mingguan dihitung bagaimana.
                jumlah_paket = math.ceil(hari / 7) if hari else 0
            else:
                jumlah_paket = hari
            rec.biaya_sewa = jumlah_paket * rec.tarif
            rec.total = rec.biaya_sewa + (rec.biaya_antar if rec.antar_jemput else 0)

    @api.onchange('paket', 'tanggal_mulai')
    def _onchange_paket_mingguan(self):
        if self.paket == 'mingguan' and self.tanggal_mulai:
            if not self.tanggal_selesai or self.tanggal_selesai <= self.tanggal_mulai:
                self.tanggal_selesai = self.tanggal_mulai + timedelta(days=7)

    # ------------------------------------------------------------------
    # Validasi
    # ------------------------------------------------------------------
    @api.constrains('tanggal_mulai', 'tanggal_selesai')
    def _cek_urutan_tanggal(self):
        for rec in self:
            if rec.tanggal_selesai <= rec.tanggal_mulai:
                raise ValidationError('Tanggal selesai harus setelah tanggal mulai.')

    @api.constrains('vehicle_id', 'tanggal_mulai', 'tanggal_selesai', 'state')
    def _cek_jadwal_bentrok(self):
        """Mencegah double booking.

        Dua jadwal pada motor yang sama bentrok kalau
        mulai_baru < selesai_lama DAN selesai_baru > mulai_lama.
        Hanya reservasi Dikonfirmasi dan Disewa yang diperiksa; draf dan batal tidak.
        """
        for rec in self:
            if rec.state not in STATUS_AKTIF:
                continue
            bentrok = self.search([
                ('id', '!=', rec.id),
                ('vehicle_id', '=', rec.vehicle_id.id),
                ('state', 'in', STATUS_AKTIF),
                ('tanggal_mulai', '<', rec.tanggal_selesai),
                ('tanggal_selesai', '>', rec.tanggal_mulai),
            ], limit=1)
            if bentrok:
                raise ValidationError(
                    '%s (%s) sudah dipesan %s s.d. %s lewat %s atas nama %s. '
                    'Pilih tanggal lain atau motor lain.' % (
                        rec.vehicle_id.rental_vehicle_name or rec.vehicle_id.display_name,
                        rec.vehicle_id.license_plate or '-',
                        bentrok.tanggal_mulai.strftime('%d-%m-%Y'),
                        bentrok.tanggal_selesai.strftime('%d-%m-%Y'),
                        bentrok.name,
                        bentrok.partner_id.name,
                    )
                )

    # ------------------------------------------------------------------
    # Nomor otomatis
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Baru') == 'Baru':
                vals['name'] = self.env['ir.sequence'].next_by_code('pav.rental.reservasi') or 'Baru'
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Tombol di formulir
    # ------------------------------------------------------------------
    def action_konfirmasi(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('Hanya reservasi berstatus Draf yang bisa dikonfirmasi.')
            motor = rec.vehicle_id
            nama_motor = '%s (%s)' % (motor.rental_vehicle_name or motor.display_name, motor.license_plate or '-')
            if motor.rental_status == 'service':
                raise ValidationError(
                    '%s sedang Servis, jadi belum bisa disewa. Pilih motor lain.' % nama_motor)
            minimal = motor.rental_minimal_hari or 1
            if rec.jumlah_hari < minimal:
                raise ValidationError(
                    '%s minimal disewa %s hari. Panjangkan tanggal selesai.' % (nama_motor, minimal))
        # Menulis status 'confirmed' memicu _cek_jadwal_bentrok.
        self.write({'state': 'confirmed'})

    def action_mulai_sewa(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError('Motor hanya bisa diserahkan dari reservasi yang sudah Dikonfirmasi.')
        # TODO Farisha (iterasi 2): catat serah terima (kondisi, BBM, helm, jas hujan, dokumen jaminan).
        self.write({'state': 'ongoing'})
        self.vehicle_id.write({'rental_status': 'rented'})

    def action_selesai(self):
        for rec in self:
            if rec.state != 'ongoing':
                raise UserError('Hanya reservasi berstatus Disewa yang bisa diselesaikan.')
        # TODO Farisha (iterasi 2): catat pengembalian dan hitung denda keterlambatan.
        self.write({'state': 'done'})
        self.vehicle_id.write({'rental_status': 'available'})

    def action_batal(self):
        for rec in self:
            if rec.state not in ('draft', 'confirmed'):
                raise UserError('Reservasi yang motornya sudah diserahkan tidak bisa dibatalkan.')
        self.write({'state': 'cancel'})

    def action_kembali_draft(self):
        self.filtered(lambda r: r.state == 'cancel').write({'state': 'draft'})
