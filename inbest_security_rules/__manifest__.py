# -*- encoding: utf-8 -*-
{
    "name": "Inbest Security Rules",
    'author': 'Soltein SA de CV',
    'version': '14.0.1.0',
    'website': 'https://www.soltein.net',
    'category': 'Tools',
    "description": """Adapt odoo rules to Inbest business workflow""",
    "depends": ['account_accountant','inbest_picking_ticket_print', 'purchase_stock', 'hr_expense', 'sale_crm', 'mrp'],
    "data": [
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
        'security/security_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

    ],
    'installable': True,
}