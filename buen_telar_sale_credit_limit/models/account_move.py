# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.tools import exception_to_unicode
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    credit_limit_id = fields.Many2one('credit.limit.catalog', string='Credit Code')
    state = fields.Selection(selection_add=[
                             ('need_authorization', 'Necesita autorizo'),
                             ('authorized', 'Authorizado')
                            ],ondelete={'need_authorization': 'set default','authorized': 'set default'})

    def action_view_mx_globals(self):
        self.ensure_one()
        if self.is_global_invoice:
            pos_orders = self.env['pos.order'].search([('global_invoice_id', '=', self.id)])
            if pos_orders:
                action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
                action['domain'] = [('is_global_payment', '=', True),
                                    ('global_invoice_id', '=', self.id)]
                return action

    def get_users_emails(self):
        # devolver la lista de las direcciones de correo de los usuarios que pertenecen al departamento
        # de creditos
        users = self.env['res.users'].search(
            [('groups_id', 'in', self.env.ref('buen_telar_credit_limit_base.group_buen_telar_authorize_credits').id)])

        emails = ""
        for user in users:
            if emails:
                emails+=','
            if user.email_formatted:
                emails+= user.email_formatted
        return emails

    def send_mail_authorization_request(self):
        try:
            subject = _("Se solicita la autorizacion de una Factura del cliente: %s.", self.partner_id.name)
            body = _("""Se solicita la autorizacion de una Factura del cliente: %(partner_name)s.
              - Importe de la factura: %(amount_total)s
              - Crédito Inicial: %(credit_limit)s
              - Crédito Disponible: %(credit_available)s 
            
            """,
                     partner_name=self.partner_id.name,
                     amount_total=self.amount_total,
                     credit_limit=self.partner_id.credit_limit,
                     credit_available=self.partner_id.credit_available, )

            emails = self.get_users_emails()

            mail_values = {
                'auto_delete': False,
                'email_from': self.env.user.email, #self.company_id.partner_id.email_formatted if self.company_id else self.env.user.email_formatted,
                'email_to': emails, #user.email_formatted,
                'body_html': body,
                'state': 'outgoing',
                'subject': subject #'%s: %s' % (user.company_id.name, self.name),
            }
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            return True

        except Exception as e:
            _logger.error("Exception while sending traceback by email: %s.\n.", e)
        pass


    def action_post(self):
        #inherit of the function from account.move to validate the partner credit
        # si ya tiene un credit_limit_id es que ya fue autorizada
        for invoice in self.filtered(lambda inv: not inv.credit_limit_id):
            partner = invoice.partner_id
            if partner.credit_available < invoice.amount_total and partner.sale_verify_credit:
                invoice.write({'state': 'need_authorization'})
                self.send_mail_authorization_request()
                action = self.sudo().env.ref('buen_telar_sale_credit_limit.action_credit_limit_warning').read()[0]
                return action
                # return {
                #             'type': 'ir.actions.client',
                #             'tag': 'display_notification',
                #             'params': {
                #                 'message': _("EL MONTO DE LA FACTURA QUE PRETENDE CONFIRMAR, EXCEDE EL VALOR DEL CRÉDITO DISPONIBLE PARA EL CLIENTE: %s. PARA CONTINUAR SOLICITE AUTORIZACIÓN DEL DEPARTAMENTO DE CRÉDITO Y COBRANZA.", partner.name),
                #                 'next': {'type': 'ir.actions.act_window_close'},
                #                 'type': 'warning',
                #                 'sticky': False,  #True/False will display for few seconds if false
                #             },
                #         }

     #    return self.sudo().env.ref('buen_telar_sale_credit_limit.action_authorization_discount_line_wizard').read()[0]

        return super(AccountMove, self).action_post()

    def action_authorize(self):
        for invoice in self.filtered(lambda inv: inv.state == 'need_authorization'):
            return self.sudo().env.ref('buen_telar_sale_credit_limit.action_authorization_discount_line_wizard').read()[0]

    def button_draft(self):
        self.write({'credit_limit_id': False})
        return super(AccountMove, self).button_draft()

    def button_cancel(self):
        self.write({'credit_limit_id': False})
        return super(AccountMove, self).button_cancel()
