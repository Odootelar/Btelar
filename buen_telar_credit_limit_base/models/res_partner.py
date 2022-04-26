# coding: utf-8
from odoo import fields, api, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_verify_credit = fields.Boolean(string="Verify Credit?")
    total_credit_consumed = fields.Float(string="Total Credit Consumed", compute="_credit_consumed_total")
    credit_available = fields.Float(string='Credit available', compute='_credit_available')
    credit_payment = fields.Float(string='Credit payment', compute='_credit_payment')

    def _credit_consumed_total(self):
        self.total_invoiced = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
        ]
        price_totals = self.env['account.move'].read_group(domain, ['amount_total'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_credit_consumed = sum(price['amount_total'] for price in price_totals if price['partner_id'][0] in child_ids)

    @api.depends('total_credit_consumed', 'credit_limit', 'credit_payment')
    def _credit_available(self):
        for record in self:
            # si el credito disponible es negativo entonces es cero
            # si si se ha consumido mas del credito disponible entonces es cero
            credit_available = record.credit_limit - record.total_credit_consumed + record.credit_payment
            record.credit_available = 0 if credit_available <= 0 or record.total_credit_consumed > record.credit_limit else credit_available

    def _credit_payment(self):
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('partner_type', '=', 'customer'),
            ('payment_type', '=', 'inbound'),
        ]
        amount_totals = self.env['account.payment'].read_group(domain, ['amount'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.credit_payment = sum(amount['amount'] for amount in amount_totals if amount['partner_id'][0] in child_ids)