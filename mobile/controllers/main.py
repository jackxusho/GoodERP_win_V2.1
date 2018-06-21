# -*- coding: utf-8 -*-
from werkzeug.contrib.sessions import FilesystemSessionStore

from mobile.http import make_response

from odoo.tools.safe_eval import safe_eval as eval

from odoo import http

from odoo.service import model
import json
from odoo.service.report import exp_render_report
from odoo.http import request


import simplejson
import os
import sys
import jinja2
import werkzeug
from xml.etree import ElementTree
from odoo.modules.registry import RegistryManager
from contextlib import closing

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

if hasattr(sys, 'frozen'):
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.mobile', 'html')

env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class MobileSupport(http.Controller):
    _VALIDATION_FIELDS = ['oauth_version',
                          'oauth_consumer_key',
                          'oauth_signature_method',
                          'oauth_nonce',
                          'oauth_timestamp',
                          ]
    _METHOD_WITH_ARGS_KWARGS = dict(
        search=dict(arg=['domain', ], kwargs=['offset', 'limit', 'order', 'context']),
        search_read=dict(arg=['domain', ], kwargs=['fields', 'offset', 'limit', 'order', 'context']),
        read=dict(arg=['fields'], kwargs=['context']),
        read_group=dict(arg=['domain', 'fields', 'groupby', ],
                        kwargs=['offset', 'limit', 'context', 'orderby', 'lazy'], ),
        default_get=dict(arg=['fields_list'], kwargs=['context'], ),
        user_has_groups=dict(arg=['groups'], kwargs=['context'], ),
        search_count=dict(arg=['domain'], kwargs=['context'], ),
        name_create=dict(arg=['name', ], kwargs=['context'], ),
        name_search=dict(arg=[], kwargs=['name', 'args', 'operator', 'limit', 'context'], ),
        fields_get=dict(arg=[], kwargs=['allfields', 'context', 'write_access', 'attributes', ], ),
        onchange=dict(arg=['values', 'field_name', 'field_onchange', ], kwargs=['context'], ),
        export_data=dict(arg=['fields_to_export', ], kwargs=['raw_data', 'context'], ),
        copy=dict(arg=['id', ], kwargs=['default', 'context'], ),
        check_field_access_rights=dict(arg=['operation', 'fields'], kwargs=['default', 'context'], ),
        check_access_rights=dict(arg=['operation', ], kwargs=['raise_exception', 'context'], ),
        check_access_rule=dict(arg=['operation', ], kwargs=['context'], ),
        import_data=dict(arg=['fields', 'datas', ],
                         kwargs=['mode', 'current_module', 'noupdate', 'filename', 'context'], ), )
    _HTTP_METHODS = dict(
        POST='create',
        GET='search_read',
        PUT='write',
        DELETE='unlink'
    )

    _GET_METHODS = ['search', 'search_read', 'read_group', 'search_count', ]

    _HTTP_REQUEST_CODE = dict(
        create=201,
        write=200,
        search_read=200,
        unlink=200
    )


    # 获取数据库支持移动操作的清单 用途 培训库，正式库 或者不同业务切换 如果只有一个，前端不显示选择
    @http.route('/mobile/db_list', type='http', auth='none', csrf=False, cors='*')
    @make_response()
    def db_list(self):
        db_list = http.db_list() or []
        db_list_by_mobile = []
        for db in db_list:
            db_manager = RegistryManager.get(db)
            with closing(db_manager.cursor()) as cr:
                cr.execute('''
                           SELECT id FROM ir_module_module
                           WHERE state = 'installed' AND name = 'mobile'
                           ''')
                if cr.fetchall():
                    db_list_by_mobile.append(db)

        return db_list_by_mobile

    @http.route('/mobile/db_login', type='http', auth='none', methods=['POST'], website=True, csrf=False, cors='*')
    @make_response()
    def db_login(self, **post):
        request.session.db = post['db']
        uid = request.session.authenticate(request.session.db, post['account'], post['passwd'])

        # 写入文件
        session_store = FilesystemSessionStore()
        session_store.save(request.session)
        # slide = request.env['slide.slide'].browse(int(slide_id))
        if uid is not False:
            return request.env['ir.http'].session_info()

        return {
            'code': '-1',
            'data': u'用户名或者密码错误。'
        }

    @http.route('/mobile/user_info', type='http', auth='none', website=True, csrf=False,
                cors='*')
    @make_response()
    def get_user_inf(self):
        # request.session.authenticate(request.session.db, 'admin', 'admin',request.session.uid)

        http.OpenERPSession.db = request.session.db
        http.OpenERPSession.uid = request.session.get('uid')
        request.disable_db = False

        # http.OpenERPSession.get_context()

        # context = dict(request._context)
        # request.env[object].with_context(context).sudo()
        user = request.env['res.users'].browse(request.session.get('uid'))
        return user;

    @http.route('/mobile', type='http', auth='none')
    def index(self):
        if not request.db or not request.session.uid:
            return werkzeug.utils.redirect('/mobile/login')

        return werkzeug.utils.redirect('/mobile/home')

    @http.route('/mobile/home', auth='public')
    def home(self):
        if not request.session.get('uid') or not request.session.uid:
            return werkzeug.utils.redirect('/mobile/login')

        template = env.get_template('index.html')
        return template.render({
            'menus': request.env['mobile.view'].search_read(
                fields=['name', 'icon_class', 'display_name', 'using_wizard'])
        })

    def _get_model(self, name):
        view = request.env['mobile.view'].search([('name', '=', name)])
        return request.env[view.model]

    def _get_fields_list(self, name):
        view = request.env['mobile.view'].search([('name', '=', name)])
        tree = ElementTree.parse(StringIO(view.arch.encode('utf-8')))
        attribs = [node.attrib for node in tree.findall('.//tree/field')]

        return {
            'left': dict(attribs[0], column=view.column_type(attribs[0].get('name', ''))),
            'center': dict(attribs[1], column=view.column_type(attribs[1].get('name', ''))),
            'right': dict(attribs[2], column=view.column_type(attribs[2].get('name', ''))),
        }

    def _get_form_fields_list(self, name):
        view = request.env['mobile.view'].search([('name', '=', name)])
        tree = ElementTree.parse(StringIO(view.arch.encode('utf-8')))

        return {node.attrib.get('name'): dict(node.attrib, column=view.column_type(node.attrib.get('name', '')))
                for node in tree.findall('.//form/field')}

    def _get_format_domain(self, name, domain):
        view = request.env['mobile.view'].search([('name', '=', name)])
        res = view.domain and eval(view.domain) or []
        res.extend([(
            item.get('name'),
            item.get('operator') or 'ilike',
            item.get('operator') and float(item.get('word')) or item.get('word')
        ) for item in domain])

        return res

    def _get_order(self, name, order):
        if len(order.split()) == 2:
            return order
        return ''

    def _parse_int(self, val):
        try:
            return int(val)
        except:
            return 0

    def _get_max_count(self, name, domain):
        # 可以考虑写成SQL语句来提高性能
        view = request.env['mobile.view'].search([('name', '=', name)])
        return len(request.env[view.model].search(domain))

    def _get_limit(self, name):
        view = request.env['mobile.view'].search([('name', '=', name)])
        return view.limit or 20

    @http.route('/mobile/get_lists', auth='public', type='http', cors='*')
    @make_response()
    def get_lists(self, name, options):
        options = simplejson.loads(options)

        model_obj = self._get_model(name)
        if options.get('type', 'tree') == 'tree':
            headers = self._get_fields_list(name)
            domain = self._get_format_domain(name, options.get('domain', ''))
            order = self._get_order(name, options.get('order', ''))
            limit = self._get_limit(name)

            return request.make_response(simplejson.dumps({
                'headers': headers,
                'max_count': self._get_max_count(name, domain),
                'values': [{
                    'left': record.get(headers.get('left').get('name')),
                    'center': record.get(headers.get('center').get('name')),
                    'right': record.get(headers.get('right').get('name')),
                    'id': record.get('id'),
                } for record in model_obj.with_context(options.get('context') or {}).search_read(
                    domain=domain, fields=map(lambda field: field.get('name'), headers.values()),
                    offset=self._parse_int(options.get('offset', 0)), limit=limit, order=order)]
            }))
        else:
            headers = self._get_form_fields_list(name)
            return request.make_response(simplejson.dumps([{
                'name': key,
                'value': value,
                'string': headers.get(key, {}).get('string'),
                'column': headers.get(key, {}).get('column'),
            } for key, value in model_obj.with_context(options.get('context') or {}).browse(self._parse_int(
                options.get('record_id'))).read(headers.keys())[0].iteritems()
            ]))

    @http.route('/mobile/get_search_view', auth='public')
    def get_search_view(self, name):
        view = request.env['mobile.view'].search([('name', '=', name)])
        tree = ElementTree.parse(StringIO(view.arch.encode('utf-8')))

        return request.make_response(simplejson.dumps(
            [dict(node.attrib, column=view.column_type(
                node.attrib.get('name', ''))) for node in tree.findall('.//search/field')]
        ))

    @http.route('/mobile/get_wizard_view', auth='public')
    def get_wizard_view(self, name):
        view = request.env['mobile.view'].search([('name', '=', name)])
        tree = ElementTree.parse(StringIO(view.arch.encode('utf-8')))

        return request.make_response(simplejson.dumps(
            [dict(node.attrib, value='') for node in tree.findall('.//wizard/field')]
        ))

    @http.route('/mobile/many2one/search', auth='public')
    def many2one_search(self, word, model, domain):
        return request.make_response(simplejson.dumps([
            {
                'id': record[0], 'value': record[1]
            } for record in request.env[model].name_search(
                word, args=eval(domain), limit=20)
        ]))

    @http.route(['/mobile/workflow/<string:object>/<int:id>/<string:signal>'],
                type="http", auth="public", csrf=False, website=True)
    @make_response()
    def call_workflow(self, object, id=None, signal=None, **kwargs):
        """
            Authenticate Request. If its valid, executes workflow
        """
        user = request.env.user
        if not user:
            return {'code': 401, 'data': 'Authentication required'}
        try:
            data = model.exec_workflow(request.cr.dbname, user.id, object, signal, id)
            if not data:
                data = '{}'
        except Exception as e:
            return {'error': {'code': 403, 'data': e.message or e.name}}
        return  data

    def evaluate(self, s):
        try:
            return eval(s)
        except Exception as e:
            try:
                return json.loads(s)
            except Exception as e:
                return s

    @http.route(['/mobile/report/<string:xml_id>/<int:id>',
                 '/mobile/report/<string:xml_id>'],
                type="http", auth="public", csrf=False, website=True)
    @make_response()
    def call_report(self, xml_id, id=None, **kwargs):
        """
            Authenticate Request. If its valid, Send report data in binary format
        """
        user = request.env.user

        ids = [id] if id else []

        if not user:
            return {'code': 401, 'data': 'Authentication required'}

        if request.httprequest.data and type(self.evaluate(request.httprequest.data)) is dict:
            kwargs.update(self.evaluate(request.httprequest.data))

        if kwargs.get('ids'):
            ids.extend(type(kwargs['ids']) is list and kwargs['ids'] or kwargs['ids'].split(','))
            ids = map(self.evaluate, ids)
        datas = []
        try:
            if not self.evaluate(kwargs.get('group')):
                for id in ids:
                    data = exp_render_report(
                        request.cr.dbname, user.id, xml_id, [id])
                    datas.append(data)
            else:
                data = exp_render_report(
                    request.cr.dbname, user.id, xml_id, id and [id] or self.evaluate(kwargs['ids']))
                datas.append(data)
        except Exception as e:
            return {'code': '-403', 'data': e.message or e.name}
        return datas

    @http.route(['/mobile/object/<string:object>/<string:method>', ],
                type="http", auth="public", csrf=False, website=True)
    @make_response()
    def perform_model_request(self, object, method, **kwargs):
        user = request.env.user
        if not user:
            return {'code': 401, 'data': 'Authentication required'}
        return self.perform_request(object, id=None, method=method, kwargs=kwargs, user=user)

    @http.route(['/mobile/object/<string:object>', \
                 '/mobile/object/<string:object>/<int:id>', \
                 '/mobile/object/<string:object>/<int:id>/<string:method>'],
                type="http", auth="public", csrf=False, website=True)
    @make_response()
    def perform_multi_request(self, object, id=None, method=None, **kwargs):
        user = request.env.user
        if not user:
            return {'code': 401, 'data': 'Authentication required'}
        return self.perform_request(object, id=id, method=method, kwargs=kwargs, user=user)

    def perform_request(self, object, method=None, id=None, kwargs={}, user=None):
        """
            Authenticate User. If valid, perform openration as per request.
        """
        datas = {}

        request_code, request_data = 200, {}
        ids, payload = [id] if id else [], {}
        arguments, k_arguments = [], {}

        if not method:
            method = self._HTTP_METHODS.get(request.httprequest.method)
            request_code = self._HTTP_REQUEST_CODE.get(method)
        if method in ('create', 'write'):
            for f in ['vals', 'args']:
                payload = kwargs.get(f) and self.evaluate(kwargs[f])
                if not payload:
                    payload = request.httprequest.data and self.evaluate(request.httprequest.data).get(f) or {}
                if payload:
                    break
            if not payload:
                payload = request.httprequest.data and self.evaluate(request.httprequest.data) or {}
            if payload:
                payload = type(payload) is list and payload[0] or payload

        if request.httprequest.data and type(self.evaluate(request.httprequest.data)) is dict:
            kwargs.update(self.evaluate(request.httprequest.data))
        if kwargs.get('ids'):
            ids.extend(type(kwargs['ids']) is list and kwargs['ids'] or kwargs['ids'].split(','))
            ids = map(self.evaluate, ids)
        if self._METHOD_WITH_ARGS_KWARGS.get(method):
            args = self._METHOD_WITH_ARGS_KWARGS.get(method)
            arguments.extend([self.evaluate(kwargs.get(arg)) for arg in args['arg']])
            k_arguments = dict([(arg, self.evaluate(kwargs[arg])) for arg in args['kwargs'] if kwargs.get(arg)])
            if method in self._GET_METHODS:
                if type(self.evaluate(kwargs.get('domain'))) is list and ids:
                    arguments[0].append(('id', 'in', ids))
                elif ids:
                    arguments[0] = [('id', 'in', ids)]
                elif not self.evaluate(kwargs.get('domain')):
                    arguments[0] = []
            elif ids:
                arguments.insert(0, ids)

        elif method in ('create', 'write'):
            arguments = [ids, payload] if ids else [payload]
            method = ids and 'write' or 'create'
            k_arguments = kwargs.get('context') and {'context': kwargs['context']} or {}
        else:
            if ids:
                arguments.append(ids)
            arguments.extend((kwargs.get('args') and self.evaluate(kwargs['args'])) or (
                    request.httprequest.data and self.evaluate(request.httprequest.data).get('args')) or [])
            k_arguments = (kwargs.get('kwargs') and self.evaluate(kwargs['kwargs'])) or (
                    request.httprequest.data and self.evaluate(request.httprequest.data).get('kwargs') or {})
        try:
            data = model.execute_kw(request.cr.dbname, user.id, object, method, arguments, kw=k_arguments)
            request.cr.commit()
            records = []
            context = dict(request._context)
            if k_arguments.get('context'):
                context.update(k_arguments['context'])
            if method in ['create', 'write']:
                env_obj = request.env[object].with_context(context).sudo()
                if id:
                    data = env_obj.search_read([('id', '=', id)])
                elif kwargs.get('ids'):
                    data = env_obj.search_read([('id', 'in', kwargs['ids'].split(','))])
                else:
                    data = env_obj.search_read([('id', '=', data)])

            data_description = request.env[object].sudo()._description.lower() or request.env[
                object].sudo()._name.lower()

            if method == 'search_count':
                data_description = 'count'

            if method == 'check_access_rights':
                data_description = 'return'

            if data and isinstance(data, list):
                if isinstance(data[0], int) or len(data) > 1:
                    datas.update({data_description: data})
                else:
                    datas.update({data_description: data[0]})
            elif data:
                if method == 'unlink':
                    datas = '{}'
                else:
                    datas.update({data_description: data})
            else:
                if method == 'search_count':
                    datas.update({data_description: 0})
                    return datas
                return {'code': -404, 'data': 'Record not found'}

        except Exception as e:
            return  {'code': -403, 'data': e.message or e.name}
        return datas
