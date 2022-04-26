# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreditLimitWarning(models.TransientModel):
    _name = "credit_limit.warning"
    _description = "Credit Limit Warning"

    @api.model
    def default_get(self, fields):
        vals = super(CreditLimitWarning, self).default_get(fields)
        if self.env.context.get('active_model') == 'sale.order':
            order = self.env['sale.order'].browse(self.env.context.get('active_id'))
            if order:
                vals['order_id'] = order.id
                vals['partner_id'] = order.partner_id.id
        return vals

    order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', string='Customer')

    def confirm(self):
        self.order_id.write({'confirm': True,})
        self.order_id.message_post(body=_("The credit to partner %s has been authorized.", self.order_id.partner_id.name))
        self.order_id.action_confirm()
