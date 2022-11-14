# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import format_date


class MovementPeriodWizard(models.TransientModel):
    _name = "movement.period.wizard"
    _description = "Wizard of Movements by Period"

    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')

    def action_movement_period(self):
        tree_view_id = self.env.ref('buen_telar_account.movement_period_tree_view').id
        search_view_id = self.env.ref('buen_telar_account.movement_period_view_search').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'list')],
            "search_view_id": [search_view_id, 'search'],
            'view_type': 'tree',
            'view_id': tree_view_id,
            'view_mode': 'tree',
            'name': _('Report of Movements by Period'),
            'res_model': 'movement.period.report',
            'domain': [],
            'display_name': _('Report of Movements by Period') + _(' from ') + format_date(self.env, self.date_start) + _(' to ') + format_date(self.env, self.date_end),
            'context': dict(self.env.context, date_start=self.date_start, date_end=self.date_end, search_default_group_by_partner=1),
            'target': 'main'
        }
        self.env['movement.period.report'].with_context(date_start=self.date_start, date_end=self.date_end).init()
        return action
