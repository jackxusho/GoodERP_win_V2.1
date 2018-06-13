# -*- coding: utf-8 -*-
from odoo import http

class GzlsdRoom(http.Controller):
    @http.route('/gzlsd_room/gzlsd_room/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    # @http.route('/gzlsd_room/gzlsd_room/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('gzlsd_room.listing', {
    #         'root': '/gzlsd_room/gzlsd_room',
    #         'objects': http.request.env['gzlsd_room.gzlsd_room'].search([]),
    #     })
    #
    # @http.route('/gzlsd_room/gzlsd_room/objects/<model("gzlsd_room.gzlsd_room"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('gzlsd_room.object', {
    #         'object': obj
    #     })