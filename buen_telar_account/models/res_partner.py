# coding: utf-8
from odoo import fields, api, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        res = []
        for rec in self:
            if rec.ref:
                res.append((rec.id, "%s - %s" % (rec.ref, rec.name)))
            else:
                res.append((rec.id, rec.name))
        return res