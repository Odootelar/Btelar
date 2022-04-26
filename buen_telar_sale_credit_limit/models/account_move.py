# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code')

    def action_view_mx_globals(self):
        self.ensure_one()
        if self.is_global_invoice:
            pos_orders = self.env['pos.order'].search([('global_invoice_id', '=', self.id)])
            if pos_orders:
                action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
                action['domain'] = [('is_global_payment','=',True),
                                    ('global_invoice_id', '=', self.id)]
                return action

    def action_post(self):
        #inherit of the function from account.move to validate the partner credit
        for invoice in self.filtered(lambda inv: not inv.credit_limit_id):
            partner = invoice.partner_id
            if partner.credit_available < invoice.amount_total and partner.sale_verify_credit:
                return self.sudo().env.ref('buen_telar_sale_credit_limit.action_authorization_discount_line_wizard').read()[0]

        return super(AccountMove, self).action_post()