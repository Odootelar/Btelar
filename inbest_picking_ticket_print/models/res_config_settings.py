# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    receipt_header = fields.Text(string='Receipt Header',
                                 help="A short text that will be inserted as a header in the printed receipt.")
    receipt_footer = fields.Text(string='Receipt Footer',
                                 help="A short text that will be inserted as a footer in the printed receipt.")
