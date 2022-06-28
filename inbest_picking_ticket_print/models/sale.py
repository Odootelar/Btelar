# -*- coding: utf-8 -*-

import logging
import num2words
from odoo import api, fields, models, _, tools
_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_reduce')
    def _get_price_reduce_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            total_price_reduce = total_price_reduce_taxinc = total_price_reduce_taxexcl = 0.0
            for line in order.order_line:
                total_price_reduce += line.price_reduce
                total_price_reduce_taxinc += line.price_reduce_taxinc
                total_price_reduce_taxexcl += line.price_reduce_taxexcl
            order.update({
                'total_price_reduce': total_price_reduce,
                'total_price_reduce_taxinc': total_price_reduce_taxinc,
                'total_price_reduce_taxexcl': total_price_reduce_taxexcl,
            })

    total_price_reduce = fields.Float(compute='_get_price_reduce_all', string='Total Price Reduce', digits='Product Price',
                                readonly=True, store=True)
    total_price_reduce_taxinc = fields.Float(compute='_get_price_reduce_all', string='Total Price Reduce tax included', digits='Product Price',
                                readonly=True, store=True)
    total_price_reduce_taxexcl = fields.Float(compute='_get_price_reduce_all', string='Total Price Reduce tax included', digits='Product Price',
                                readonly=True, store=True)

    approved_by_id = fields.Many2one('res.users', string='Aprobado por', readonly=True, store=True, index=True, tracking=True)

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
            'date_order': fields.Datetime.now(),
            'approved_by_id': self.env.uid
        }

    def action_draft(self):
        # al volver a borrador se debe eliminar el usuario que aprobo la cotizacion
        self.write({'approved_by_id': False})
        return super(SaleOrder, self).action_draft()


    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning(
                "The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.currency_id.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang_code = self.env.user.lang or self.env.context.get('lang')
        lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', lang_code)])
        if self.currency_id.name == 'USD':
            value_unit = 'USD'
        else:
            value_unit = 'M.N'
        amount_words = tools.ustr(_('{amt_value} {amt_word} {amt_decimal}/100 {amt_value_unit}')).format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_decimal=fractional_value,
            amt_word=self.currency_id.currency_unit_label,
            amt_value_unit=value_unit,
        )
        amount_words = amount_words.upper()
        if lang_code == 'es_MX':
            amount_words = amount_words.replace('DOLLARS', 'DOLARES')
        return amount_words.replace(" 0/", " 00/")

    # def get_order_tax_value_in_receipt(self):
    #     fiscal_position_id = self.fiscal_position_id
    #     taxes_dict = {}
    #     for line in self.order_line:
    #         taxes = line.tax_id.filtered(lambda t: t.company_id.id == self.company_id.id)
    #         if fiscal_position_id:
    #             taxes = fiscal_position_id.map_tax(taxes, line.product_id, self.partner_id)
    #         price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = taxes.compute_all(price, self.pricelist_id.currency_id, line.product_uom_qty, product=line.product_id,
    #                                   partner=self.partner_id or False)['taxes']
    #         for each_line_tax in taxes:
    #             taxes_dict.setdefault(each_line_tax['name'], 0.0)
    #             taxes_dict[each_line_tax['name']] += each_line_tax['amount']
    #     return taxes_dict
    #
    def get_total_discount_in_receipt(self):
        total_discount = 0.0
        for line in self.order_line:
            if line.discount:
                total_discount += (line.product_uom_qty * line.price_unit - line.price_subtotal)
        return total_discount

    def get_total_before_discount_in_receipt(self):
        total = 0.0
        for line in self.order_line:
            total += (line.product_uom_qty * line.price_unit)
        return total
    #
    #
    #
    # def get_receipt_header(self):
    #     return "Header ...."
    #
    # def get_receipt_footer(self):
    #     return "Footeer"