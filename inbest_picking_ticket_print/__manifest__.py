# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': 'Stock Ticket Receipt from Backend',
    'category': 'Stock',
    'version': "14.0.1.0",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    'summary': """This Module allows you to generate Ticket Receipt(PDF report) from backend.""",
    'description': """
        This Module allows you to generate Ticket Receipt(PDF report) from backend.
        * Allows user to print PDF Ticket Receipt on Picking.
    """,
    'depends': ['sale_management', 'sale_stock'],
    'data': [
        'views/report.xml',
        "views/res_company_view.xml",
        "views/sale_order_view.xml",
        'views/picking_ticket_receipt_pdf_template.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: