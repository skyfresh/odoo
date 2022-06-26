# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lot = fields.Many2one('fileopening', "Lot")
    ref1 = fields.Char('Ref1')
    delivery_date = fields.Date('Order Delivery Date')
    pickup_date = fields.Date('Pickup Date')

    bills = fields.Many2many('account.move', compute='_compute_bills')

    def _compute_bills(self):
        for order in self:
            order.bills = self.env['account.move'].search(
                [('lot', '=', order.lot.id), ('move_type', '=', 'in_invoice')])

    def create_bill(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.sudo().read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_move_type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'default_lot': self.lot.id,
        }

        res = self.env.ref('account.view_move_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
        return result