# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import ustr
from collections import defaultdict

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # total_receivable = fields.Float(string="Total Receivable", compute="_compute_total_receivable")
    exceeded_amount = fields.Float(string="Exceeded Amount")
    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code')
    confirm = fields.Boolean(string='Confirm', default=False)

    def action_confirm(self):

        for order in self.filtered(lambda so: not so.confirm):
            partner = order.partner_id
            if partner.credit_available < order.amount_total and partner.sale_verify_credit:
                action = self.sudo().env.ref('buen_telar_sale_credit_limit.action_credit_limit_warning').read()[0]
                return action
        return super(SaleOrder, self).action_confirm()