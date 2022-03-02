# -*- coding: utf-8 -*-

{
    'name': "ERP Pos amount words",
    'version': "14.0.1.0",
    'category': "Pos",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        Pos amount words
    """,
    'depends': [
        'point_of_sale',
    ],
    'data': [
        "views/assets.xml",
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    'installable': True,
}