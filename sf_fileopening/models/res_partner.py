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