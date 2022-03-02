# -*- coding: utf-8 -*-

import hashlib

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    credit_catalog_ids = fields.Many2many(
        'credit.limit.catalog', string="Catalogs",
        help='Catalogs can access in to the PoS session')


class PosOrder(models.Model):
    _inherit = "pos.order"

    credit_catalog_code = fields.Char(string="Catalog Code", required=False, default='')
    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code')

