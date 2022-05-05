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
            # credit_available = record.credit_limit - record.total_credit_consumed + record.credit_payment
            # record.credit_available = 0 if credit_available <= 0 or record.total_credit_consumed > record.credit_limit else credit_available
            company_currency_id = record.company_id.currency_id or self.env.company.currency_id
            # amount_payment_posted = 0.00
            amount_invoice_posted = 0.00

            # domain_payment = [
            #     ('partner_id', '=', record.id),
            #     ('partner_type', '=', 'customer'),
            #     ('payment_type', '=', 'inbound'),
            #     ('state', '=', 'posted')
            # ]
            # for payment in self.env['account.payment'].search(domain_payment):
            #     if payment.currency_id.id == company_currency_id.id:
            #         amount_payment_posted += payment.amount
            #     else:
            #         amount_payment_posted += payment.currency_id._convert(payment.amount, company_currency_id, payment.company_id, fields.Date.today(), round=False)

            domain_invoice = [
                ('partner_id', '=', record.id),
                ('state', '=', 'posted'),
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('payment_state', 'in', ('not_paid', 'in_payment', 'partial'))
            ]

            for invoice in self.env['account.move'].search(domain_invoice):
                if invoice.currency_id.id == company_currency_id.id:
                    amount_invoice_posted += invoice.amount_residual
                else:
                    amount_invoice_posted += invoice.currency_id._convert(invoice.amount_residual, company_currency_id, invoice.company_id, fields.Date.today(), round=False)

            credit_available = record.credit_limit - amount_invoice_posted
            record.credit_available = 0 if credit_available < 0 else credit_available

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
