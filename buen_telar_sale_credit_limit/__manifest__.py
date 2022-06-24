# -*- coding: utf-8 -*-

{
    'name': "Sale management Credit Control",
    'version': "14.0.1.0",
    'category': "Sale",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        Sale management Credit Control
    """,
    'depends': [
        'buen_telar_credit_limit_base',
        'sale_management',
    ],
    'data': [
        "security/ir.model.access.csv",
        "wizard/authorization_credit.xml",
        "wizard/credit_limit_warning.xml",
        "views/account_move_views.xml",
        "views/menu.xml",
        "views/sale_order_views.xml",
        "report/sale_report_templates.xml",
    ],
    'installable': True,
}