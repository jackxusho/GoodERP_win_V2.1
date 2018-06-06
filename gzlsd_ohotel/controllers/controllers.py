# -*- coding: utf-8 -*-
from odoo import http

# class GzlsdOhotel(http.Controller):
#     @http.route('/gzlsd_ohotel/gzlsd_ohotel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gzlsd_ohotel/gzlsd_ohotel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gzlsd_ohotel.listing', {
#             'root': '/gzlsd_ohotel/gzlsd_ohotel',
#             'objects': http.request.env['gzlsd_ohotel.gzlsd_ohotel'].search([]),
#         })

#     @http.route('/gzlsd_ohotel/gzlsd_ohotel/objects/<model("gzlsd_ohotel.gzlsd_ohotel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gzlsd_ohotel.object', {
#             'object': obj
#         })