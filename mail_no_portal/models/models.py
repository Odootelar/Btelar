#-*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_access_action(self, access_uid=None):
        return {}


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_access_action(self, access_uid=None):
        return {}
