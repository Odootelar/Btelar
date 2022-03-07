# -*- coding: utf-8 -*-

{
    'name': "Point of Sale Credit Control",
    'version': "14.0.1.0",
    'category': "Pos",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        Point of Sale Credit Control
    """,
    'depends': [
        'buen_telar_credit_limit_base',
        'point_of_sale',
    ],
    'data': [

        "views/templates.xml",
        "views/menu.xml",
        "views/pos_credit_limit_views.xml",
    ],
    'qweb': [
        'static/src/xml/Popups/CreditInputPopup.xml',
    ],

    'installable': True,
}
