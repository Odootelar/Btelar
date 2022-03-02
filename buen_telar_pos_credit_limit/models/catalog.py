# -*- coding: utf-8 -*-

import hashlib

from odoo import api, fields, models, _


class CreditLimitCatalog(models.Model):
    _inherit = "credit.limit.catalog"

    def get_code_hashed(self):
        # Apply visibility filters (record rules)
        visible_catalogs_ids = self.search([('id', 'in', self.ids)])
        catalog_data = self.sudo().search_read([('id', 'in', visible_catalogs_ids.ids)], ['code', 'name'])

        for c in catalog_data:
            c['name'] = c['code'] if c['code'] else ''
            c['code'] = hashlib.sha1(c['code'].encode('utf8')).hexdigest() if c['code'] else ''
        return catalog_data
