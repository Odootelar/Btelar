# -*- coding: utf-8 -*-

import hashlib

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    credit_catalog_ids = fields.Many2many('credit.limit.catalog', string="Catalogs",
        help='Catalogs can access in to the PoS session')

    def es_valido(self, code):
        # para determinar si el codigo de credito es valido para este pos
        # code = int(code)
        pos = self.credit_catalog_ids.search([('code','=', code)])
        if pos:
            return True
        else:
            return False


class PosOrder(models.Model):
    _inherit = "pos.order"

    credit_catalog_code = fields.Char(string="Catalog Code", required=False, default='')
    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code')

    def set_credit_limit_code(self, code):
        """Override this method to introduce action when setting no tip."""
        # self.ensure_one()
        catalog = self.env['credit.limit.catalog'].search([('code', '=', code)])
        self.write({
            'credit_catalog_code': code,
            'credit_limit_id': catalog.id,
            })