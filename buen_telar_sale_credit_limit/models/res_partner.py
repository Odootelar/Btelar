# coding: utf-8
from odoo import fields, api, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_verify_credit = fields.Boolean(string="Verify Credit?")
