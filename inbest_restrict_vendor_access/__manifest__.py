# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Inbest - Restrict Vendor Access",
    'summary': "",
    'description': """
    This modulo Restrict salers access over suppliers.
    """,
     'category': 'Sale',
    'sequence': 190,
    'author': "Soltein SA de CV",
    'website': "https://www.soltein.net",
    'version': '1.0',
    'depends': [
        'sale',
    ],
    'data': [
        'security/security.xml',
        'views/res_partner_view.xml',
    ],
    'application': False,
    'auto_install': False,
}
