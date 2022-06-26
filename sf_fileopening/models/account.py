# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_commission = fields.Boolean()

    def open_bill_form(self):
        try:
            form_view_id = self.env.ref('account.view_move_form').id
        except Exception as e:
            form_view_id = False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view_id,
            'res_id': self.id,
            'res_model': 'account.move',
            'target': 'current',
        }

    @api.depends('invoice_origin')
    def _default_sale_order(self):
        for move in self:
            # _logger.info('default_sale_order1')
            if move.invoice_origin:
                # _logger.info('default_sale_order2' + str(move.invoice_origin))

                orders = self.env['sale.order'].search([('name', 'like', move.invoice_origin)])
                for order in orders:
                    # _logger.info('_default_sale_order - order')
                    move.sale_order = order.id

                # _logger.info(move.sale_order)
                if not move.sale_order:
                    previous_moves = self.env['account.move'].search([('name', 'like', move.invoice_origin)])
                    _logger.info('_default_sale_order - move1')
                    for previousMove in previous_moves:
                        _logger.info('_default_sale_order - move2')

                        if previousMove.sale_order:
                            move.sale_order = previousMove.sale_order.id

            if not move.lot and move.sale_order and move.sale_order.lot:
                move.lot = move.sale_order.lot

    lot = fields.Many2one('fileopening', "Lot")
    sale_order = fields.Many2one(comodel_name='sale.order', string='Sale Order', store=True,
                                 default=_default_sale_order)

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        res._default_sale_order()
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for move in self:
            if move.lot:
                move.lot._compute_totals()
        return res
