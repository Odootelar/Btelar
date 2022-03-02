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
        "views/menu.xml",
    ],
    'installable': True,
}