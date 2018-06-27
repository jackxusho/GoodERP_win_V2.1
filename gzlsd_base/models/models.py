# -*- coding: utf-8 -*-

from odoo import models, fields, http, api
from odoo.exceptions import UserError


class Site(models.Model):
    _name = 'rm.site'
    _rec_name = 'name'

    name = fields.Char(string=u'分店名称', required=True)
    parent_site_id = fields.Many2one(string=u'上级门店', comodel_name='rm.site',
                                     domain="[('id', '!=', id)]")
    google_map = fields.Char(string="Map")
    img = fields.Many2many('ir.attachment', string=u"门店图片")
    company_id = fields.Many2one(string=u'所属公司', required=True, comodel_name='res.company',
                                 domain="[('is_company', '=', True)]",
                                 default=lambda self: self.env.user.company_id)

    @api.one
    @api.constrains('parent_site_id')
    def _check_parent_site_id(self):
        '''上级门店不能选择自己和下级的门店'''
        if self.parent_site_id:
            childs = self.env['rm.site'].search(
                [('parent_site_id', '=', self.id)])
            print(type(childs))
            if self.parent_site_id in (childs, self.id):
                raise UserError(u'上级门店不能选择他自己或者他的下级门店')


class Building(models.Model):
    _name = 'rm.building'
    _rec_name = 'name'

    name = fields.Char(string=u'建筑名称', required=True)
    sort_id = fields.Integer(string=u'排序值', required=True)
    img = fields.Many2many('ir.attachment', string=u"建筑图片")
    site_id = fields.Many2one(string=u'所属门店', required=True, comodel_name='res.site')


class Floor(models.Model):
    _name = 'rm.floor'
    _rec_name = 'name'

    name = fields.Char(string=u'楼层名字', required=True)
    code = fields.Char(string=u"楼层代码", required=True, )
    sort_id = fields.Integer(string=u'排序值', required=True)


# 房间类型
class RoomType(models.Model):
    _name = 'rm.room_type'
    _rec_name = 'name'

    RM_FUNC_TYPE = [
        ('G', u'客房'),
        ('D', u'假房'),
        ('F', u'功能房')
    ]

    name = fields.Char(string=u'房型名称', required=True)
    code = fields.Char(string=u"房型代码", required=True)
    sort_id = fields.Integer(string=u'排序值', required=True)
    func_dummy = fields.Selection(string="房型标记", selection=RM_FUNC_TYPE, required=True, default='G',
                                  track_visibility='aways')
    rate = fields.Float(string="标准房价", required=True)
    site_id = fields.Many2one(string=u'所属门店', required=True, comodel_name='res.site')
    img = fields.Binary(string=u"建筑图片")


# 房间特性分类
class RoomFeatureCat(models.Model):
    _name = 'rm.room_feature_cat'
    _rec_name = 'name'

    name = fields.Char(string=u'名称', required=True)


# 房间特性
class RoomFeature(models.Model):
    _name = 'rm.room_feature'
    _rec_name = 'name'

    name = fields.Char(string=u'名称', required=True)
    feature_cat_id = fields.Many2one(string=u'所属分类', required=True,
                                     comodel_name='rm.room_feature_cat'
                                     )
