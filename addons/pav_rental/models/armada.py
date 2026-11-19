from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    rental_vehicle_name = fields.Char(
        string='Nama Kendaraan',
        help='Masukkan nama atau tipe kendaraan, misalnya Vario 160.',
    )

    rental_image = fields.Image(
        string='Foto Kendaraan',
        max_width=1920,
        max_height=1920,
    )

    rental_brand_id = fields.Many2one(
        comodel_name='fleet.vehicle.model.brand',
        string='Merek Kendaraan',
        ondelete='restrict',
    )

    rental_vehicle_type = fields.Selection(
        selection=[
            ('car', 'Mobil'),
            ('bike', 'Motor'),
        ],
        default='bike',
        required=True,
    )

    rental_status = fields.Selection(
        selection=[
            ('available', 'Tersedia'),
            ('rented', 'Disewa'),
            ('service', 'Servis'),
        ],
        string='Status Penyewaan',
        default='available',
        required=True,
        tracking=True,
    )

    rental_notes = fields.Text(
        string='Keterangan Kendaraan',
        help='Catatan tambahan mengenai kendaraan untuk keperluan penyewaan.',
    )

    rental_currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        string='Mata Uang Sewa',
    )

    rental_tarif_harian = fields.Monetary(
        string='Tarif Harian',
        currency_field='rental_currency_id',
    )

    rental_tarif_mingguan = fields.Monetary(
        string='Tarif Mingguan',
        currency_field='rental_currency_id',
    )

    rental_minimal_hari = fields.Integer(
        string='Minimal Sewa (hari)',
        default=1,
        help='Contoh: Beat 2014 minimal disewa 2 hari.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vehicle_name = vals.get('rental_vehicle_name')
            brand_id = vals.get('rental_brand_id')

            if vehicle_name and brand_id:
                vehicle_model = self.env['fleet.vehicle.model'].search([
                    ('name', '=', vehicle_name),
                    ('brand_id', '=', brand_id),
                ], limit=1)

                if not vehicle_model:
                    vehicle_model = self.env['fleet.vehicle.model'].create({
                        'name': vehicle_name,
                        'brand_id': brand_id,
                    })

                vals['model_id'] = vehicle_model.id

        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)

        if 'rental_vehicle_name' in vals or 'rental_brand_id' in vals:
            for vehicle in self:
                if vehicle.rental_vehicle_name and vehicle.rental_brand_id:
                    vehicle_model = self.env['fleet.vehicle.model'].search([
                        ('name', '=', vehicle.rental_vehicle_name),
                        ('brand_id', '=', vehicle.rental_brand_id.id),
                    ], limit=1)

                    if not vehicle_model:
                        vehicle_model = self.env['fleet.vehicle.model'].create({
                            'name': vehicle.rental_vehicle_name,
                            'brand_id': vehicle.rental_brand_id.id,
                        })

                    super(FleetVehicle, vehicle).write({
                        'model_id': vehicle_model.id,
                    })

        return result
