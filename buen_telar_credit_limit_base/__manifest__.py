# -*- coding: utf-8 -*-

{
    'name': "Sale Credit Control Base",
    'version': "14.0.1.0",
    'category': "Pos",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        Sale Credit Control Base
    """,
    'depends': [
        'account',
    ],
    'data': [
        "security/credit_security.xml",
        "security/ir.model.access.csv",
        "views/credit_limit_views.xml",
        "views/res_partner_view.xml",

    ],
    'installable': True,
}
