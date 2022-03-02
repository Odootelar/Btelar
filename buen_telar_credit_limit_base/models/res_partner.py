# coding: utf-8
from odoo import fields, api, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_verify_credit = fields.Boolean(string="Verify Credit?")
    total_credit_consumed = fields.Float(string="Total Credit Consumed", compute="_credit_consumed_total")

    def _credit_consumed_total(self):
        self.total_invoiced = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
        ]
        price_totals = self.env['account.invoice.report'].read_group(domain, ['price_subtotal'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_credit_consumed = sum(price['price_subtotal'] for price in price_totals if price['partner_id'][0] in child_ids)
