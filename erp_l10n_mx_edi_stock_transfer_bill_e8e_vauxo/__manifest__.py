# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Stock Delivery Bill CFDI",
    "version": "15.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "base",
        "l10n_mx_edi_stock_extended_40",
    ],
    "data": [
        'data/cfdi_cartaporte.xml',
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
