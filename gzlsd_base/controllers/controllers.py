# -*- coding: utf-8 -*-
from odoo import http

class GzlsdRoom(http.Controller):
    @http.route('/gzlsd_base/gzlsd_base/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    # @http.route('/gzlsd_base/gzlsd_base/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('gzlsd_base.listing', {
    #         'root': '/gzlsd_base/gzlsd_base',
    #         'objects': http.request.env['gzlsd_base.gzlsd_base'].search([]),
    #     })
    #
    # @http.route('/gzlsd_base/gzlsd_base/objects/<model("gzlsd_base.gzlsd_base"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('gzlsd_base.object', {
    #         'object': obj
    #     })