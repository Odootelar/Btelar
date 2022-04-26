# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AuthorizationPartnerCredit(models.TransientModel):
    _name = "authorization.partner.credit"
    _description = "Authorization Partner Credit"

    @api.model
    def default_get(self, fields):
        vals = super(AuthorizationPartnerCredit, self).default_get(fields)
        if self.env.context.get('active_model') == 'account.move':
            invoice = self.env['account.move'].browse(self.env.context.get('active_id'))
            if invoice:
                vals['invoice_id'] = invoice.id
                vals['partner_id'] = invoice.partner_id.id
        return vals

    invoice_id = fields.Many2one('account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Customer')
    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code', required=True)

    def confirm(self):
        self.invoice_id.write({
            'credit_limit_id': self.credit_limit_id.id,
        })
        self.invoice_id.message_post(body=_("The credit to partner %s has been authorized.", self.invoice_id.partner_id.name))
        self.invoice_id.action_post()