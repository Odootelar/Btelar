# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_view_mx_globals(self):
        self.ensure_one()
        if self.is_global_invoice:
            pos_orders = self.env['pos.order'].search([('global_invoice_id', '=', self.id)])
            if pos_orders:
                action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
                action['domain'] = [('is_global_payment','=',True),
                                    ('global_invoice_id', '=', self.id)]
                return action

