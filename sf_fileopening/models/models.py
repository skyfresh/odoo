# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
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
    
    bills = fields.Many2many('account.invoice', compute='_compute_bills')
    
    @api.multi
    def _compute_bills(self):
        for order in self:
            order.bills = self.env['account.invoice'].search([('lot', '=', order.lot.id),('type', '=', 'in_invoice')])

    @api.multi
    def create_bill(self):
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'default_lot': self.lot.id,
            'company_id': self.company_id.id
        }

        res = self.env.ref('account.invoice_supplier_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
        return result
        
            
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
        res._default_sale_order()
        return res
    
    @api.multi
    def write(self,vals):
        res = super(AccountInvoice, self).write(vals)
        for invoice in self:
             if invoice.lot:
                invoice.lot._compute_totals()
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

    freight_type = fields.Selection([
            ('air', 'Air'),
            ('sea', 'Sea'),
            ('road', 'Road'),
        ],
        string='Freight Type')    
    
    @api.multi
    @api.depends('imp_exp','sequence','freight_type')
    def _compute_lot(self):
        for file in self:
            lot = 'FR'
            if(file.freight_type == 'air' or not file.freight_type): lot = lot + 'A'
            if(file.freight_type == 'sea'): lot = lot + 'S'
            if(file.freight_type == 'road'): lot = lot + 'R'
            if(file.imp_exp == 'import'): lot = lot + 'I'
            if(file.imp_exp == 'export'): lot = lot + 'E'
            if(file.imp_exp == 'other'): lot = lot + 'O'
            if(file.sequence): lot = lot + file.sequence
            file.lot = lot

    mawb = fields.Char('MAWB / MBL')
    hawb = fields.Char('HAWB / HBL')

    pol = fields.Char('POL')
    pod = fields.Char('POD')
    stop = fields.Char('STOP')

    airline = fields.Char('Airline / Seafreight Company')
    flight = fields.Char('Flight / Vessel')

    etd = fields.Date('ETD')
    eta = fields.Date('ETA')
    delivery_date = fields.Date('DEL DATE')
    
    po_client = fields.Char('PO Client #')
    container_type = fields.Selection(
        [
            ('lcl', 'LCL'),
            ('fcl', 'FCL')
        ],
        string='Container Type')
    
    
    container_number = fields.Char('Container #')
    seal_number = fields.Char('Seal #')
    
    customs_type = fields.Selection(
        [
            ('ta', 'TA'),
            ('ima', 'IMA')
        ],
        string='Customs Type')
    customs_ima_number = fields.Char('IMA #')

    consignee = fields.Many2one('res.partner',string='Consignee')
    shipper = fields.Many2one('res.partner',string='Shipper')
    notify = fields.Many2one('res.partner',string='Notify')

    incoterm = fields.Many2one('account.incoterms',string='Incoterm')

    op_agent = fields.Many2one('res.partner',string='Operation Agent')
    sale_agent = fields.Many2one('res.partner',string='Sale Agent')
    
    sales = fields.One2many('account.invoice', compute='_compute_sales')
    
    @api.multi
    def _compute_sales(self):
        for file in self:
            file.sales = self.env['account.invoice'].search([('lot', '=', file.lot),('type', 'in', ['out_invoice','out_refund'])])
    
    
    bills = fields.One2many('account.invoice', compute='_compute_bills')
    
    @api.multi
    def _compute_bills(self):
        for file in self:
            file.bills = self.env['account.invoice'].search([('lot', '=', file.lot),('type', 'in', ['in_invoice','in_refund'])])
            

    imp_exp = fields.Selection(
        [
            ('import', 'Import'),
            ('export', 'Export'),
            ('other', 'Other')
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

    af = fields.Boolean('A/F / O/F')

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
    
    
    partner_id = fields.Many2one('res.partner', string="Customer", compute='_compute_totals', store=True)
    total_paid = fields.Float('Total Paid', compute='_compute_totals', store=True)
    total_received = fields.Float('Total Received', compute='_compute_totals', store=True)
    margin = fields.Float('Margin', compute='_compute_totals', store=True)

    invoice_total = fields.Float('Invoice Total', compute='_compute_totals', store=True)
    bill_total = fields.Float('Bill Total', compute='_compute_totals', store=True)
    theorical_margin = fields.Float('Theorical Margin', compute='_compute_totals', store=True)
    
    @api.multi
    def _compute_totals(self):
        company = self.env.user.company_id
        date = datetime.today()
        for file in self:

            invoices = self.env['account.invoice'].search([('lot', '=', file.id)])
            total_paid = 0
            total_received = 0
            invoice_total = 0
            bill_total = 0
            theorical_margin = 0
            partner_id = None
            for invoice in invoices:
                #_logger.info("test"+str(invoice.id))
                company_currency = invoice.company_id.currency_id
                if invoice.type == 'out_invoice':
                    partner_id = invoice.sale_order.partner_id
                    invoice_total = invoice_total + invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                    if invoice.state == 'paid':
                        total_received = total_received + invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                        
                if invoice.type == 'in_invoice':
                    bill_total = bill_total + invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                    if invoice.state == 'paid':
                        total_paid = total_paid + invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                        
                if invoice.type == 'out_refund':
                    invoice_total = invoice_total - invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                    if invoice.state == 'paid':
                        total_received = total_received - invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                        
                if invoice.type == 'in_refund':
                    bill_total = bill_total - invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                    if invoice.state == 'paid':
                        total_paid = total_paid - invoice.currency_id._convert(invoice.amount_untaxed, company_currency, company, date)
                        
            file.partner_id = partner_id
            file.total_received = total_received
            file.total_paid = total_paid
            file.bill_total = bill_total
            file.invoice_total = invoice_total
            file.margin = file.total_received - file.total_paid
            file.theorical_margin = invoice_total - bill_total
            
