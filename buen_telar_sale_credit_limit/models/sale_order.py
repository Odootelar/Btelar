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

    # @api.depends('partner_id', 'partner_id.credit_limit', 'order_line.invoice_lines')
    # def _compute_total_receivable(self):
    #     for sale in self:
    #         if sale.partner_id.credit_limit:
    #             sale.total_receivable = sale.partner_id.credit_limit

    def action_confirm(self):
        for order in self.filtered(lambda so: not so.credit_limit_id):
            partner = order.partner_id
            if partner.credit_available < order.amount_total and partner.sale_verify_credit:
                action = self.sudo().env.ref('buen_telar_sale_credit_limit.action_authorization_discount_line_wizard').read()[0]
                return action
                # raise ValidationError(_(
                #     'You have been put on hold due to exceeding your credit limit. '
                #     'Please contact administration for further guidance. \n Thank You'))

        return super(SaleOrder, self).action_confirm()
