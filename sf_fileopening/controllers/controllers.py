# -*- coding: utf-8 -*-
from odoo import http

# class SfFileopening(http.Controller):
#     @http.route('/sf_fileopening/sf_fileopening/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sf_fileopening/sf_fileopening/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sf_fileopening.listing', {
#             'root': '/sf_fileopening/sf_fileopening',
#             'objects': http.request.env['sf_fileopening.sf_fileopening'].search([]),
#         })

#     @http.route('/sf_fileopening/sf_fileopening/objects/<model("sf_fileopening.sf_fileopening"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sf_fileopening.object', {
#             'object': obj
#         })