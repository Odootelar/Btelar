# -*- coding: utf-8 -*-
# from odoo import http


# class Autorizaciones(http.Controller):
#     @http.route('/autorizaciones/autorizaciones/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/autorizaciones/autorizaciones/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('autorizaciones.listing', {
#             'root': '/autorizaciones/autorizaciones',
#             'objects': http.request.env['autorizaciones.autorizaciones'].search([]),
#         })

#     @http.route('/autorizaciones/autorizaciones/objects/<model("autorizaciones.autorizaciones"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('autorizaciones.object', {
#             'object': obj
#         })
