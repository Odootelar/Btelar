# -*- coding: utf-8 -*-

{
    'name': "Buen Telar Account",
    'version': "14.0.1.0",
    'category': "Account",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        Buen Telar Account
    """,
    'depends': [
        'account',
    ],
    'data': [

        "security/ir.model.access.csv",
        "report/movement_period_views.xml",
        "wizard/wzd_movement_period.xml",

    ],
    'installable': True,
}