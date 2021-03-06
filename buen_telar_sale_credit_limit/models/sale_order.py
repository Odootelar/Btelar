# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import ustr
from collections import defaultdict
from odoo.tools.misc import formatLang, get_lang
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_note_sale(self):
        note = "Este documento tiene vigencia de METRAJE de 24hrs.\n" + "CAMBIO DE PRECIO sin previo aviso."
        return note

    # total_receivable = fields.Float(string="Total Receivable", compute="_compute_total_receivable")
    exceeded_amount = fields.Float(string="Exceeded Amount")
    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code')
    confirm = fields.Boolean(string='Confirm', default=False)
    price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce', digits='Product Price')
    delivery_address = fields.Char(compute='_get_delivery_address')
    note_sale = fields.Text(string='Notas', default=_get_note_sale)

    def action_confirm(self):
        for order in self.filtered(lambda so: not so.confirm):
            partner = order.partner_id
            if partner.credit_available < order.amount_total and partner.sale_verify_credit:
                action = self.sudo().env.ref('buen_telar_sale_credit_limit.action_credit_limit_warning').read()[0]
                return action
        return super(SaleOrder, self).action_confirm()

    @api.depends('order_line.price_unit', 'order_line.discount', 'order_line.product_uom_qty')
    def _get_price_reduce(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                total += (line.product_uom_qty * line.price_unit) - line.price_subtotal
            order.price_reduce = total

    @api.depends('partner_id')
    def _get_delivery_address(self):
        for order in self:
            order.delivery_address = order.partner_id.child_ids.search([('type', '=', 'delivery')], limit=1).contact_address


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    modify_price = fields.Boolean('Modify price', default=False)

    @api.onchange('price_unit')
    def change_price_unit(self):
        if not self.product_id:
            return
        if self.product_id.lst_price != self.price_unit:
            self.modify_price = False
        else:
            self.modify_price = True

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            if self.modify_price:
                self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)
