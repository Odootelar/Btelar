# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    l10n_mx_invoice_internal_transfer = fields.Boolean(string='Use on Invoice transfer')
    rfc_generic_invoice_transfer = fields.Char(string='Generic RFC for Invoice transfer',
                                               default='XAXX010101000')
    fiscal_regime_rfc_generic_invoice_transfer = fields.Char(string='Generic RFC Fiscal Regime for Invoice transfer',
                                               default='616')

class Picking(models.Model):
    _inherit = "stock.picking"

    l10n_mx_invoice_internal_transfer = fields.Boolean(related='picking_type_id.l10n_mx_invoice_internal_transfer',
                                 string="Use on Invoice for internal transfer", compute_sudo=True)

    def button_validate(self):
        if any(self.mapped(lambda rrp: rrp.l10n_mx_invoice_internal_transfer
                                       and rrp.l10n_mx_edi_transport_type == '00'
                                       and not rrp.partner_id)):
            raise ValidationError(_('Please select contact for document!'))
        return super(Picking, self).button_validate()

    def l10n_mx_edi_action_cancel_transfer_invoice(self):
        self.l10n_mx_edi_action_cancel_delivery_guide()


