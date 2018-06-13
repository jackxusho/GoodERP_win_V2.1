# -*- coding: utf-8 -*-

from odoo import models, fields,http,api


class rm_building(models.Model):
    _name = 'rm.rm_building'
    _rec_name = 'name'

    # default_company_id =0;
    # for p in http.request.env['res.users'].search([('id','=',self.uid)]):
    name = fields.Char(string=u'建筑名称', required=True)
    sort_id = fields.Integer(string=u'排序值', required=True)
    img = fields.Binary(string=u"建筑图片")
    company_id = fields.Many2one(string=u'所属公司', required=True, comodel_name='res.partner',
                                 domain="[('is_company', '=', True)]",
                                 default=lambda self: self.env.user.company_id
                                 )


class rm_floor(models.Model):
    _name = 'rm.rm_floor'
    _rec_name = 'name'

    name = fields.Char(string=u'楼层名字', required=True)
    code = fields.Char(string=u"楼层代码", required=True, )
    sort_id = fields.Integer(string=u'排序值', required=True)
    company_id = fields.Many2one(string=u'所属公司', required=True, comodel_name='res.partner',
                                 domain="[('is_company', '=', True)]",
                                 default=lambda self: self.env.user.company_id)


class rm_room_type(models.Model):
    _name = 'rm.rm_room_type'
    _rec_name = 'name'

    RM_FUNC_TYPE = [
        ('G', u'客房'),
        ('D', u'假房'),
        ('F', u'功能房')
    ]

    state = fields.Selection([('new', u'招生'), ('start', u'已开课'),
                              ('end', u'已结束')], string=u"课程状态", default='new',
                             track_visibility='aways')

    name = fields.Char(string=u'房型名称', required=True)
    code = fields.Char(string=u"房型代码", required=True, )
    sort_id = fields.Integer(string=u'排序值', required=True)
    func_dummy = fields.Selection(string="房型标记", selection=RM_FUNC_TYPE, required=True, default='G',
                                  track_visibility='aways')
    rate = fields.Float(string="标准房价", required=True)
    company_id = fields.Many2one(string=u'所属公司', required=True, comodel_name='res.partner',
                                 domain="[('is_company', '=', True)]",
                                 default=lambda self: self.env.user.company_id)
    img = fields.Binary(string=u"建筑图片")
