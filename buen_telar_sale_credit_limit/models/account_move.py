# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo import tools
from odoo.tools import exception_to_unicode
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
                               default=fields.Date.context_today,
                                states={'draft': [('readonly', False)]})
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

    @api.model
    def notify_channel_follow(self, author, partner_to, action_message, channel):
        MailChannel = self.env['mail.channel'].sudo()
        MailMessage = self.env['mail.message'].sudo()
        if not author:
            author = self.env.ref('base.user_admin').sudo()
        if not channel:
            channel_find = MailChannel.sudo(author).channel_get_and_minimize([partner_to.id])
            channel = MailChannel.browse(channel_find['id'])
        text_action = action_message
        ctx = dict(self.env.context)
        ctx.update({'mail_notify_force_send': False})
        ctx.update({
            'default_author_id': author.partner_id.id,
            'default_reply_to': '%s <%s>' % (tools.ustr(author.partner_id.name), author.partner_id.email),
            'default_email_from': '%s <%s>' % (tools.ustr(author.partner_id.name), author.partner_id.email)
        })

        new_message = MailMessage.create({
            'body': text_action,
            'model': 'mail.channel',
            'res_id': channel.id,
            'parent_id': False,
            'author_id': author.partner_id.id,
            'message_type': 'comment',
            'subject': False,
            'partner_ids': [],
            'subtype_id': 1
        })
        self.env.cr.commit()
        channel._broadcast([partner_to.id])
        return True

    def notify_channel(self, user, action_message):
        author = self.env.ref('base.user_admin').sudo()
        users_channel = [(4, user.partner_id.id),(4, author.partner_id.id)]

        channel_ref_id = self.env['mail.channel'].sudo().create({
                'name': _('Production Order # %s'),
                'channel_type': 'chat',
                'email_send': False,
                'public': 'private',
                'channel_partner_ids': users_channel
            })
        #     self.channel_id = channel_ref_id.id
        # else:
        #     if user.sudo().partner_id.id not in self.channel_id.sudo().channel_partner_ids.ids:
        #         self.channel_id.sudo().write({'channel_partner_ids': users_channel})

        # channel_id = self.channel_id
        self.env['mail.message'].sudo().create({
            'body': action_message,
            'model': 'mail.channel',
            'res_id': channel_ref_id.id,
            'parent_id': False,
            'author_id': self.env.user.partner_id.id,
            'message_type': 'comment',
            'subject': False,
            'partner_ids': users_channel,
            'subtype_id': 1
        })
        self.env.cr.commit()
        channel_ref_id._broadcast(user.partner_id.id)

    def send_notification_authorization_request(self):
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

        users = self.env['res.users'].search(
            [('groups_id', 'in', self.env.ref('buen_telar_credit_limit_base.group_buen_telar_authorize_credits').id)])

        # ctx = dict(self.env.context)
        # ctx.update({'mail_notify_force_send': False})

        notification_ids = []
        partner_ids = []
        for user in users:
            # self.notify_channel(user, body)
            if user.partner_id:
                partner_ids.append(user.partner_id.id)
                notification_ids.append((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox',
                    'is_read': False,}))

        # notifications = []
        # for mail_channel_info in mail_channels_info:
        #     notifications.append([(self._cr.dbname, 'res.partner', operator.partner_id.id), mail_channel_info])
        # self.env['bus.bus'].sendmany(notifications)


        self.message_post(body=body,
                          message_type='notification',
                          subtype_xmlid='mail.mt_comment',
                          author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)

        # partner_ids.append(self.env.user.partner_id.id)
        # # # odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # channel_info = self.env['mail.channel'].channel_get(partner_ids)
        # channel = self.browse(channel_info['id'])
        # channel.sudo().message_post(body=body, author_id=self.env.user.partner_id.id, message_type="comment",
        #                             subtype_xmlid="mail.mt_comment")

    def action_post(self):
        #inherit of the function from account.move to validate the partner credit
        # si ya tiene un credit_limit_id es que ya fue autorizada
        for invoice in self.filtered(lambda inv: not inv.credit_limit_id):
            partner = invoice.partner_id
            if partner.credit_available < invoice.amount_total and partner.sale_verify_credit:
                invoice.write({'state': 'need_authorization'})
                # self.send_mail_authorization_request()
                self.send_notification_authorization_request()
                action = self.sudo().env.ref('buen_telar_sale_credit_limit.action_credit_limit_warning').read()[0]
                return action

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
