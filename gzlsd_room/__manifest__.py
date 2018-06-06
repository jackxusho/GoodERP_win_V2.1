# -*- coding: utf-8 -*-
{
    'name': "GZLSD 房间管理",
    'author': "广州菱致计算机科技有限公司",
    'website': "www.sglsd.com",
    'category': 'gzlsd',
    'summary': '通用房间管理模块',
    "description":
    '''
    该模块实现通用的房间管理，房型管理，房价管理，房间状态管理，未来房态查询，以及外部调用接口。。
    ''',
    'version': '0.1',
    'depends': ["mail"],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'AGPL-3',
}
