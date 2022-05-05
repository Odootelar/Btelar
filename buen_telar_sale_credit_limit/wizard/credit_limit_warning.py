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
        if self.env.context.get('active_model') == 'account.move':
            invoice = self.env['account.move'].browse(self.env.context.get('active_id'))
            if invoice:
                vals['invoice_id'] = invoice.id
                vals['partner_id'] = invoice.partner_id.id
        return vals

    invoice_id = fields.Many2one('account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Customer')

    # def confirm(self):
    #     self.order_id.write({'confirm': True,})
    #     self.order_id.message_post(body=_("The credit to partner %s has been authorized.", self.order_id.partner_id.name))
    #     self.order_id.action_confirm()
