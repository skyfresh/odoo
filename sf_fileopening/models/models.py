# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_code = fields.Char('Customer Code')
    is_consignee = fields.Boolean('Is Consignee')
    is_notify = fields.Boolean('Is Notify')
    is_shipper = fields.Boolean('Is Shipper')
    is_op_agent = fields.Boolean('Is Operation Agent')
    is_sale_agent = fields.Boolean('Is Sale Agent')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lot = fields.Many2one('fileopening', "Lot")
    ref1 = fields.Char('Ref1')
    delivery_date = fields.Date('Delivery Date')
    pickup_date = fields.Date('Pickup Date')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order = fields.Many2one(compute='_get_origin_sale_order_id', comodel_name='sale.order', string='Sale Order', store=True)

    @api.depends('origin')
    def _get_origin_sale_order_id(self):
        origin = self.env['sale.order'].search([('name', '=', self.origin)])
        if(origin): self.sale_order = origin[0].id

class Fileopening(models.Model):
    _name = 'fileopening'
    _description = "FileOpening"
    _rec_name = 'lot'

    sequence = fields.Char('Sequence', readonly=True)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('fileopening.code') or '/'
        vals['sequence'] = seq
        return super(Fileopening, self).create(vals)

    lot = fields.Char('Lot Number', compute='_compute_lot', store=True)

    @api.depends('imp_exp','sequence')
    def _compute_lot(self):
        lot = 'FRA'
        if(self.imp_exp == 'import'): lot = lot + 'I'
        if(self.imp_exp == 'export'): lot = lot + 'E'
        if(self.sequence): lot = lot + self.sequence
        self.lot = lot

    mawb = fields.Char('MAWB')
    hawb = fields.Char('HAWB')

    pol = fields.Char('POL')
    pod = fields.Char('POD')
    stop = fields.Char('STOP')

    airline = fields.Char('Airline')
    flight = fields.Char('Flight')

    etd = fields.Date('ETD')
    eta = fields.Date('ETA')
    delivery_date = fields.Date('DEL DATE')

    consignee = fields.Many2one('res.partner',string='Consignee')
    shipper = fields.Many2one('res.partner',string='Shipper')
    notify = fields.Many2one('res.partner',string='Notify')

    incoterm = fields.Many2one('account.incoterms',string='Incoterm')

    op_agent = fields.Many2one('res.partner',string='Operation Agent')
    sale_agent = fields.Many2one('res.partner',string='Sale Agent')

    imp_exp = fields.Selection(
        [
            ('import', 'Import'),
            ('export', 'Export')
        ],
        name='Import/Export',
    )

    phyto = fields.Boolean('Phyto')
    truck = fields.Selection(
        [
            ('truck1', 'truck1'),
            ('truck2', 'truck2'),
            ('truck3', 'truck3'),
            ('truck4', 'truck4'),
            ('truck5', 'truck5')
        ],
        name='Truck',
    )

    af = fields.Boolean('A/F')

    currency = fields.Many2one('res.currency',string='Currency', domain="[('active', '=', True)]")

    exchange_rate = fields.Float('Exchange Rate')

    palettized = fields.Boolean('Palettized')

    box_amount = fields.Integer('Box Amount')
    palette_amount = fields.Integer('Palette Amount')

    weight_gross = fields.Float('Gross Weight')
    weight_net = fields.Float('Net Weight')
    weight_chargeable = fields.Float('Chargeable Weight')

    cbm  = fields.Float('CBM')

    product = fields.Char('Product')
    brand = fields.Char('Brand')
    qc = fields.Boolean('QC')
    temperature_required = fields.Boolean('Temperature Required')

    remarks = fields.Text('Remarks')