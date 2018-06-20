# -*- coding: utf-8 -*-

from odoo import models, fields, http, api


class rm_building(models.Model):
    _name = 'mobile.menu'
    _order = 'menu_id asc'

    APP_TYPE = [
        ('H', u'酒店'),
        ('M', u'月子中心'),
        ('O', u'养老院')
    ]

    menu_id = fields.Integer(string=u'菜单ID', required=True)
    p_id = fields.Integer(string=u'上级菜单ID' )
    name = fields.Char(string=u'菜单名称', required=True)
    route = fields.Char(string=u'前端路由')
    icon = fields.Char(string=u'图标', required=True)
    color = fields.Char(string=u'图标颜色', required=True, default='#409EFF')
    app_type = fields.Selection(string="菜单归属", selection=APP_TYPE, required=True, default='M',
                                track_visibility='aways')

# 继承groups 增加移动menu权限
class ResPartner(models.Model):
    _inherit = 'res.groups'

    @api.model
    def _is_teacher(self):
        return self.env.context.get('is_teacher')

    # 提取xml字段里面定义的老师标记，决定是否默认为老师 default=一个函数
    mobile_menu_access = fields.Many2many(string=u"移动端菜单", comodel_name='mobile.menu')
