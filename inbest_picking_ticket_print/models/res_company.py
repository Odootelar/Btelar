# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import api, fields, models, _
from odoo.modules.module import get_module_resource
from odoo.modules.module import get_resource_path


class ResCompany(models.Model):
    _inherit = "res.company"

    fax = fields.Char('Fax')