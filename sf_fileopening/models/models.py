# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


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
    
    @api.multi
    @api.depends('origin')
    def _default_sale_order(self):
        for invoice in self:
            _logger.info('default_sale_order1')
            if(invoice.origin):
                _logger.info('default_sale_order2' + str(invoice.origin))
                
                orders = self.env['sale.order'].search([('name', 'like', invoice.origin)])
                for order in orders:
                    _logger.info('_default_sale_order - order')
                    invoice.sale_order = order.id
                
                _logger.info(invoice.sale_order)
                if not invoice.sale_order:
                    previousInvoices = self.env['account.invoice'].search([('number', 'like', invoice.origin)])
                    _logger.info('_default_sale_order - invoice1')
                    for previousInvoice in previousInvoices:
                        _logger.info('_default_sale_order - invoice2')
                        
                        if previousInvoice.sale_order:
                            invoice.sale_order = previousInvoice.sale_order.id
                            
            if not invoice.lot and invoice.sale_order and invoice.sale_order.lot:
                invoice.lot = invoice.sale_order.lot
                
    
    lot = fields.Many2one('fileopening', "Lot")
    sale_order = fields.Many2one(comodel_name='sale.order', string='Sale Order', store=True, default=_default_sale_order)

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        print('hello')
        res._default_sale_order()
        return res


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
    
    total_paid = fields.Float('Total Paid', compute='_compute_totals')
    total_received = fields.Float('Total Received', compute='_compute_totals')
    
    margin = fields.Float('Margin', compute='_compute_totals')

    @api.multi
    def _compute_totals(self):
        for file in self:
            invoices = self.env['account.invoice'].search([('lot', '=', file.id)])
            total_paid = 0
            total_received = 0
            for invoice in invoices:
                if invoice.type == 'out_invoice' and invoice.state == 'paid':
                    total_received = total_received + invoice.amount_total
                if invoice.type == 'in_invoice' and invoice.state == 'paid':
                    total_paid = total_received + invoice.amount_total
            file.total_received = total_received
            file.total_paid = total_paid
            file.margin = file.total_received - file.total_paid
