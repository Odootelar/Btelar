# coding: utf-8
from odoo import fields, api, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier = fields.Boolean(string="Supplier", default=False)
    customer = fields.Boolean(string="Customer", default=False)

    def get_restrict_access_domain(self):
        extra_domain = []
        if not self.env.user.has_group('inbest_restrict_vendor_access.group_supplier_manager'):
            extra_domain.append(('supplier', '=', False))

        return extra_domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        extra_domain = self.get_restrict_access_domain()
        if extra_domain:
            args += extra_domain
        return super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)



    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        args = args or []
        extra_domain = self.get_restrict_access_domain()

        if extra_domain:
            args += extra_domain

        res = super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res