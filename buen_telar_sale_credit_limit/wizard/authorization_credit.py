# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


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

    def get_email(self):
        # devolver la lista de las direcciones de correo de los partners seguidores de la Factura
        # por defecto el cliente y el usuarios que crea la factura
        emails = ""
        for partner in self.invoice_id.message_follower_ids.mapped('partner_id'):
            if emails:
                emails+=','
            if partner.email:
                emails+= partner.email_formatted
        return emails

    def send_mail_authorization_approve(self):
        try:
            subject = _("Se ha autorizado la Factura del cliente: %s.", self.invoice_id.partner_id.name)
            body = _("""Se ha autorizado la Factura del cliente: %(partner_name)s.
              - Importe de la factura: %(amount_total)s
              
            """,    partner_name=self.invoice_id.partner_id.name,
                     amount_total=self.invoice_id.amount_total,)

            emails = self.get_email()

            mail_values = {
                'auto_delete': False,
                'email_from': self.env.user.email,
                # self.company_id.partner_id.email_formatted if self.company_id else self.env.user.email_formatted,
                'email_to': emails,  # user.email_formatted,
                'body_html': body,
                'state': 'outgoing',
                'subject': subject  # '%s: %s' % (user.company_id.name, self.name),
            }
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            return True
        except Exception as e:
            _logger.error("Exception while sending traceback by email: %s.\n.", e)
        pass
    
    def send_notification_authorization_approve(self):
        body = _("""Se ha autorizado la Factura del cliente: %(partner_name)s.
                      - Importe de la factura: %(amount_total)s
                    """, partner_name=self.invoice_id.partner_id.name,
                 amount_total=self.invoice_id.amount_total, )
        notification_ids = []
        for partner in self.invoice_id.message_follower_ids.mapped('partner_id'):
            notification_ids.append((0, 0, {
                'res_partner_id': partner.id,
                'notification_type': 'inbox'}))

        self.invoice_id.message_post(body=body,
                          message_type='notification',
                          subtype_xmlid='mail.mt_comment',
                          author_id=self.env.user.partner_id.id,
                          notification_ids = notification_ids)


    def confirm(self):
        self.invoice_id.write({
            'credit_limit_id': self.credit_limit_id.id,
            'state': 'authorized',
        })
        self.send_notification_authorization_approve()
        # self.invoice_id.message_post(body=_("The credit to partner %s has been authorized.", self.invoice_id.partner_id.name))
        # self.invoice_id.action_post()