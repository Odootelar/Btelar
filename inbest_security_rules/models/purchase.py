# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import SUPERUSER_ID, _, api, fields, models, registry


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        for order in self:
            if order.with_user(SUPERUSER_ID).state not in ['draft', 'sent']:
                continue
            order.with_user(SUPERUSER_ID)._add_supplier_to_product()
            # Deal with double validation process
            if order.with_user(SUPERUSER_ID)._approval_allowed():
                order.with_user(SUPERUSER_ID).button_approve()
            else:
                order.with_user(SUPERUSER_ID).write({'state': 'to approve'})
            if order.with_user(SUPERUSER_ID).partner_id not in order.with_user(SUPERUSER_ID).message_partner_ids:
                order.with_user(SUPERUSER_ID).message_subscribe([order.partner_id.id])
        return True
        # print("hola lolo")
        # self.with_user(SUPERUSER_ID).button_confirm()
        # return super(PurchaseOrder, self).with_user(SUPERUSER_ID).button_confirm()

