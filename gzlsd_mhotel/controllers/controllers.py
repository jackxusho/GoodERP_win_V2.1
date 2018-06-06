# -*- coding: utf-8 -*-
from odoo import http

# class GzlsdMhotel(http.Controller):
#     @http.route('/gzlsd_mhotel/gzlsd_mhotel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gzlsd_mhotel/gzlsd_mhotel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gzlsd_mhotel.listing', {
#             'root': '/gzlsd_mhotel/gzlsd_mhotel',
#             'objects': http.request.env['gzlsd_mhotel.gzlsd_mhotel'].search([]),
#         })

#     @http.route('/gzlsd_mhotel/gzlsd_mhotel/objects/<model("gzlsd_mhotel.gzlsd_mhotel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gzlsd_mhotel.object', {
#             'object': obj
#         })