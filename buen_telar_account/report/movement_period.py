# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class MovementPeriod(models.Model):
    _name = "movement.period.report"
    # _auto = False
    _order = 'to_order, move_type desc'

    document = fields.Char(string='Type')
    to_order = fields.Integer(string='To order')
    partner_id = fields.Many2one('res.partner', string='Customer')
    ref_partner = fields.Char(related='partner_id.ref')
    reference = fields.Char(string='Reference')
    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    total_move = fields.Float(string='Charges')
    total_payment = fields.Float(string='Credits')
    move_type = fields.Selection([('entry', 'Journal Entry'), ('out_invoice', 'Customer Invoice')], string='Move type')
    days = fields.Integer(string='Days passed', compute='_compute_days')
    name = fields.Char(string='Name')
    invoice_origin = fields.Char(string='Invoice origin')
    classification = fields.Char(string='Classification', compute='_compute_classification')

    @api.depends('date_start', 'reference', 'move_type')
    def _compute_days(self):
        for record in self:
            if record.move_type == 'entry':
                date_invoice = self.search([('name', '=', record.reference)], limit=1).date_start
                if record.date_start and date_invoice:
                    days = (record.date_start - date_invoice).days
                    record.days = days if days > 0 else False
                else:
                    record.days = False
            else:
                record.days = False

    @api.depends('move_type')
    def _compute_classification(self):
        for record in self:
            if record.move_type == 'out_invoice':
                sale_order = self.env['sale.order'].search([('name', '=', record.invoice_origin)])
                record.classification = sale_order.client_order_ref if sale_order else False
            else:
                record.classification = False

    def init(self):
        # para lograr este reporte hay que aplica cierto nivel de logica de negocio
        # para esto la solucion fue filtrar los registros antes de mostrarlo en el reporte
        # tools.drop_view_if_exists(self.env.cr, self._table)
        date_start = fields.Date.from_string(self.env.context.get('date_start', fields.Date.to_string(fields.Datetime.now().date())))
        date_end = fields.Date.from_string(self.env.context.get('date_end', fields.Date.to_string(fields.Datetime.now().date())))

        date_start = '{}{}{}'.format("'", date_start, "'")
        date_end = '{}{}{}'.format("'", date_end, "'")
        # Se limpia la tabla para mostrar los resultados de esta peticion esto es similar a
        # tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" delete from movement_period_report""")
        #  se ejecuta la consulta para obtener los registros con algunas condidiones
        self.env.cr.execute(""" 
                SELECT
                --invoice.payment_state,
                --payment_invoice.payment_id,
                 CASE WHEN invoice.move_type = 'entry' THEN
                    invoice.id
                ELSE
                    payment_invoice.move_id
                END AS to_order,
                invoice.id AS id,
                CASE WHEN invoice.move_type = 'entry' THEN
                        (SELECT name FROM l10n_mx_edi_payment_method WHERE id=invoice.l10n_mx_edi_payment_method_id)
                    ELSE
                        (SELECT name FROM account_journal WHERE id=invoice.journal_id)
                    END AS document,

                invoice.ref AS reference,
                invoice.partner_id AS partner_id,
                CASE WHEN invoice.move_type = 'entry' THEN
                        invoice.date
                    ELSE
                        invoice.invoice_date
                    END AS date_start,  
                CASE WHEN invoice.move_type = 'entry' THEN
                        invoice.date
                    ELSE
                        invoice.invoice_date_due
                    END AS date_end,
                CASE WHEN invoice.move_type = 'out_invoice' THEN invoice.amount_total END AS total_move,
                CASE WHEN invoice.move_type = 'entry' THEN invoice.amount_total END AS total_payment,
                invoice.move_type AS move_type,
                invoice.name AS name,
                invoice.invoice_origin AS invoice_origin
                FROM account_move  AS invoice
                LEFT JOIN (SELECT
                payment.move_id,payment.id as payment_id,
                invoice.id as invoice_id,
                invoice.move_type
                FROM account_payment payment
                JOIN account_move move ON move.id = payment.move_id
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
                JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
                JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                JOIN account_account account ON account.id = line.account_id
                WHERE account.internal_type IN ('receivable', 'payable')
                AND invoice.move_type in ('out_invoice')
                GROUP BY payment.move_id,payment.id,invoice.id, invoice.move_type) as payment_invoice on payment_invoice.invoice_id=invoice.id
                WHERE (CASE WHEN invoice.move_type = 'entry' THEN
                            invoice.date
                        ELSE
                            invoice.invoice_date
                        END ) >= """+str(date_start)+"""
                AND (CASE WHEN invoice.move_type = 'entry' THEN
                            invoice.date
                        ELSE
                            invoice.invoice_date
                        END ) <= """+str(date_end)+"""
                AND invoice.move_type in ('entry','out_invoice')
                AND invoice.state not in ('draft','cancel')
                AND invoice.journal_id not in (SELECT id FROM account_journal WHERE type='general')
        """)
        # Los resultados de la consulta deben ser filtrados  ya que las facturas no pueden repetirse para que aparezcan
        # correctamente ordenados
        factlist = []
        for move_inv in self.env.cr.dictfetchall():
            if move_inv['id'] not in factlist:
                factlist.append(move_inv['id'])
                # en el mismo proceso se crea el registro en la tabla para mostrar el reporte
                self.create(dict(move_inv))
                # print(move_inv)

        # self._cr.execute("""
        #     CREATE or REPLACE view movement_period_report as (
        #          SELECT
        #         --invoice.payment_state,
        #         --payment_invoice.payment_id,
        #          CASE WHEN invoice.move_type = 'entry' THEN
        #             invoice.id
        #         ELSE
        #             payment_invoice.move_id
        #         END AS to_order,
        #         invoice.id AS id,
        #         CASE WHEN invoice.move_type = 'entry' THEN
        #                 (SELECT name FROM l10n_mx_edi_payment_method WHERE id=invoice.l10n_mx_edi_payment_method_id)
        #             ELSE
        #                 (SELECT name FROM account_journal WHERE id=invoice.journal_id)
        #             END AS document,
        #
        #         invoice.ref AS reference,
        #         invoice.partner_id AS partner_id,
        #         CASE WHEN invoice.move_type = 'entry' THEN
        #                 invoice.date
        #             ELSE
        #                 invoice.invoice_date
        #             END AS date_start,
        #         CASE WHEN invoice.move_type = 'entry' THEN
        #                 invoice.date
        #             ELSE
        #                 invoice.invoice_date_due
        #             END AS date_end,
        #         CASE WHEN invoice.move_type = 'out_invoice' THEN invoice.amount_total END AS total_move,
        #         CASE WHEN invoice.move_type = 'entry' THEN invoice.amount_total END AS total_payment,
        #         invoice.move_type AS move_type,
        #         invoice.name AS name,
        #         invoice.invoice_origin AS invoice_origin
        #         FROM account_move  AS invoice
        #         LEFT JOIN (SELECT
        #         payment.move_id,payment.id as payment_id,
        #         invoice.id as invoice_id,
        #         invoice.move_type
        #         FROM account_payment payment
        #         JOIN account_move move ON move.id = payment.move_id
        #         JOIN account_move_line line ON line.move_id = move.id
        #         JOIN account_partial_reconcile part ON
        #         part.debit_move_id = line.id
        #         OR
        #         part.credit_move_id = line.id
        #         JOIN account_move_line counterpart_line ON
        #         part.debit_move_id = counterpart_line.id
        #         OR
        #         part.credit_move_id = counterpart_line.id
        #         JOIN account_move invoice ON invoice.id = counterpart_line.move_id
        #         JOIN account_account account ON account.id = line.account_id
        #         WHERE account.internal_type IN ('receivable', 'payable')
        #         AND invoice.move_type in ('out_invoice')
        #         GROUP BY payment.move_id,payment.id,invoice.id, invoice.move_type) as payment_invoice on payment_invoice.invoice_id=invoice.id
        #         WHERE (CASE WHEN invoice.move_type = 'entry' THEN
        #                     invoice.date
        #                 ELSE
        #                     invoice.invoice_date
        #                 END ) >= """+str(date_start)+"""
        #         AND (CASE WHEN invoice.move_type = 'entry' THEN
        #                     invoice.date
        #                 ELSE
        #                     invoice.invoice_date
        #                 END ) <= """+str(date_end)+"""
        #         AND invoice.move_type in ('entry','out_invoice')
        #         AND invoice.state not in ('draft','cancel')
        #         AND invoice.journal_id not in (SELECT id FROM account_journal WHERE type='general')
        #
        #
        #         );
        # """)