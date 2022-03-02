# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



from werkzeug.urls import url_encode


class CreditLimitCatalog(models.Model):
    _name = "credit.limit.catalog"
    _inherit = ['mail.thread']
    _description = "Credit limit Catalog"
    _order = 'id desc'

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Title', required=True)
    code = fields.Char(string='Code', required=True)


