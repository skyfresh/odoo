# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

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

    @api.depends('imp_exp', 'sequence', 'freight_type')
    def _compute_lot(self):
        for file in self:
            lot = 'FR'
            if (file.freight_type == 'air' or not file.freight_type): lot = lot + 'A'
            if (file.freight_type == 'sea'): lot = lot + 'S'
            if (file.freight_type == 'road'): lot = lot + 'R'
            if (file.imp_exp == 'import'): lot = lot + 'I'
            if (file.imp_exp == 'export'): lot = lot + 'E'
            if (file.imp_exp == 'other'): lot = lot + 'O'
            if (file.sequence): lot = lot + file.sequence
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
            ('fcl_20', 'FCL 20'),
            ('fcl_40', 'FCL 40'),
            ('fcl_45', 'FCL 45'),
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

    consignee = fields.Many2one('res.partner', string='Consignee')
    consignee_text = fields.Char(related='consignee.name', string='Consignee', store=True)

    shipper = fields.Many2one('res.partner', string='Shipper')
    shipper_text = fields.Char(related='shipper.name', string='Shipper', store=True)

    notify = fields.Many2one('res.partner', string='Notify')
    notify_text = fields.Char(related='notify.name', string='Notify', store=True)

    incoterm = fields.Many2one('account.incoterms', string='Incoterm')

    op_agent = fields.Many2one('res.partner', string='Operation Agent')
    op_agent_text = fields.Char(related='op_agent.name', string='Operation Agent', store=True)

    sale_agent = fields.Many2one('res.partner', string='Sale Agent')
    sale_agent_text = fields.Char(related='sale_agent.name', string='Sale Agent', store=True)

    sales = fields.One2many('account.move', compute='_compute_sales')
    sales_text = fields.Html(compute='_compute_sales')

    def _compute_sales(self):
        for file in self:
            sales = self.env['account.move'].sudo().search(
                [('lot', '=', file.lot), ('move_type', 'in', ['out_invoice', 'out_refund'])])

            sales_text = '<table style="width: 100%"><tr><td>Number</td><td>Partner</td><td>Total</td><td>Payment Status</td><td>Status</td></tr>'
            for move in sales:
                sales_text = sales_text + '<tr><td>'+move.name+'</td><td>'+move.partner_id.name+'</td><td>'+str(move.amount_total_signed)+' '+move.company_currency_id.symbol+'</td><td>'+move.payment_state+'</td><td>'+move.state+'</td></tr>'

            sales_text = sales_text + '</table>'
            file.sales = sales
            file.sales_text = sales_text

    bills = fields.One2many('account.move', compute='_compute_bills')
    bills_text = fields.Html(compute='_compute_bills')

    commissions = fields.One2many('account.move', compute='_compute_bills')
    commissions_text = fields.Html(compute='_compute_bills')

    def _compute_bills(self):
        for file in self:
            bills = self.env['account.move'].sudo().search(
                [('lot', '=', file.lot), ('move_type', 'in', ['in_invoice', 'in_refund'])])

            bills_text = '<table style="width: 100%"><tr><td>Number</td><td>Partner</td><td>Total</td><td>Payment Status</td><td>Status</td></tr>'
            for move in bills:
                bills_text = bills_text + '<tr><td>'+move.name+'</td><td>'+move.partner_id.name+'</td><td>'+str(move.amount_total_signed)+' '+move.company_currency_id.symbol+'</td><td>'+move.payment_state+'</td><td>'+move.state+'</td></tr>'
            bills_text = bills_text + '</table>'

            file.bills = bills
            file.bills_text = bills_text

            commissions = self.env['account.move'].sudo().search(
                [('lot', '=', file.lot), ('move_type', 'in', ['in_invoice', 'in_refund']), ('is_commission','=',True)])

            commissions_text = '<table style="width: 100%"><tr><td>Number</td><td>Partner</td><td>Total</td><td>Payment Status</td><td>Status</td></tr>'
            for move in commissions:
                commissions_text = commissions_text + '<tr><td>'+move.name+'</td><td>'+move.partner_id.name+'</td><td>'+str(move.amount_total_signed)+' '+move.company_currency_id.symbol+'</td><td>'+move.payment_state+'</td><td>'+move.state+'</td></tr>'
            commissions_text = commissions_text + '</table>'

            file.commissions = commissions
            file.commissions_text = commissions_text

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

    currency = fields.Many2one('res.currency', string='Currency', domain="[('active', '=', True)]")

    exchange_rate = fields.Float('Exchange Rate')

    palettized = fields.Boolean('Palettized')

    box_amount = fields.Integer('Box Amount')
    palette_amount = fields.Integer('Palette Amount')

    weight_gross = fields.Float('Gross Weight')
    weight_net = fields.Float('Net Weight')
    weight_chargeable = fields.Float('Chargeable Weight')

    cbm = fields.Float('CBM')

    product = fields.Char('Product')
    brand = fields.Char('Brand')
    qc = fields.Boolean('QC')
    temperature_required = fields.Boolean('Temperature Required')

    remarks = fields.Text('Remarks')

    partner_id = fields.Many2one('res.partner', string="Customer", store=True)
    total_paid = fields.Float('Total Paid', compute='_compute_totals', store=True)
    total_received = fields.Float('Total Received', compute='_compute_totals', store=True)
    margin = fields.Float('Margin', compute='_compute_totals', store=True)

    invoice_total = fields.Float('Invoice Total', compute='_compute_totals', store=True)
    bill_total = fields.Float('Bill Total', compute='_compute_totals', store=True)
    theorical_margin = fields.Float('Theorical Margin', compute='_compute_totals', store=True)

    commission_paid = fields.Float('Commission Paid', compute='_compute_totals', store=True)
    theorical_commission = fields.Float('Theorical Commission', compute='_compute_totals', store=True)
    margin_after_commission = fields.Float('Margin After Commission', compute='_compute_totals', store=True)
    theorical_margin_after_commission = fields.Float('Theorical Margin After Commission', compute='_compute_totals', store=True)

    def _compute_totals(self):
        company = self.env.user.company_id
        date = datetime.today()
        for file in self:

            invoices = self.env['account.move'].sudo().search([('lot', '=', file.id), ('state', '!=', 'cancel'), ('is_commission', '=', False)])
            total_paid = 0
            total_received = 0
            invoice_total = 0
            bill_total = 0
            partner_id = None

            for invoice in invoices:
                company_currency = invoice.company_id.currency_id
                if invoice.move_type == 'out_invoice':

                    partner_id = invoice.sale_order.partner_id
                    invoice_total = invoice_total + invoice.currency_id._convert(invoice.amount_untaxed,
                                                                                 company_currency, company, date)
                    if invoice.payment_state == 'paid':
                        total_received = total_received + invoice.currency_id._convert(invoice.amount_untaxed,
                                                                                       company_currency, company, date)

                if invoice.move_type == 'in_invoice':
                    bill_total = bill_total + invoice.currency_id._convert(invoice.amount_untaxed, company_currency,
                                                                           company, date)
                    if invoice.payment_state == 'paid':
                        total_paid = total_paid + invoice.currency_id._convert(invoice.amount_untaxed, company_currency,
                                                                               company, date)

                if invoice.move_type == 'out_refund':
                    invoice_total = invoice_total - invoice.currency_id._convert(invoice.amount_untaxed,
                                                                                 company_currency, company, date)
                    if invoice.payment_state == 'paid':
                        total_received = total_received - invoice.currency_id._convert(invoice.amount_untaxed,
                                                                                       company_currency, company, date)

                if invoice.move_type == 'in_refund':
                    bill_total = bill_total - invoice.currency_id._convert(invoice.amount_untaxed, company_currency,
                                                                           company, date)
                    if invoice.payment_state == 'paid':
                        total_paid = total_paid - invoice.currency_id._convert(invoice.amount_untaxed, company_currency,
                                                                               company, date)

            if not file.partner_id and partner_id:
                file.partner_id = partner_id

            file.total_received = total_received
            file.total_paid = total_paid
            file.bill_total = bill_total
            file.invoice_total = invoice_total
            file.margin = file.total_received - file.total_paid
            file.theorical_margin = invoice_total - bill_total

            commissions = self.env['account.move'].sudo().search(
                [('lot', '=', file.id), ('state', '!=', 'cancel'), ('is_commission', '=', True)])

            commission_paid = 0
            theorical_commission = file.theorical_margin * file.partner_id.commission_percent

            for commission in commissions:
                company_currency = commission.company_id.currency_id

                if commission.move_type == 'in_invoice':
                    if invoice.payment_state == 'paid':
                        commission_paid = commission_paid + commission.currency_id._convert(commission.amount_untaxed, company_currency,
                                                                               company, date)

                if commission.move_type == 'in_refund':
                    if commission.payment_state == 'paid':
                        commission_paid = commission_paid - commission.currency_id._convert(commission.amount_untaxed, company_currency,
                                                                               company, date)

            file.theorical_commission = theorical_commission
            file.theorical_margin_after_commission = invoice_total - bill_total - theorical_commission

            file.commission_paid = commission_paid
            file.margin_after_commission = file.total_received - file.total_paid - file.commission_paid

    def compute_totals(self):
        for file in self:
            file._compute_totals()