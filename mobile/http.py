# -*- coding: utf-8 -*-
import types
from functools import wraps
import json

from odoo.http import request
from odoo.tools.safe_eval import safe_eval


class make_response:

    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                headers = {"Access-Control-Allow-Credentials": "true",
                           'Access-Control-Allow-Origin': 'http://192.168.3.8'}
                result_data = func(*args, **kwargs)
                # 如果是返回错误代码和描述
                if isinstance(result_data, types.DictType) and 'code' in result_data:
                    return request.make_response(json.dumps(result_data), headers=headers)

                # 格式化返回结果
                result = {
                    'code': '0',
                    'data': result_data
                }

                # json返回
                return request.make_response(json.dumps(result), headers=headers)
            except Exception, e:
                return request.make_response(json.dumps({'code': '500', 'data': str(e)}), headers=headers)

        return wrapper


def eval_request_params(kwargs):
    for k, v in kwargs.iteritems():
        try:
            kwargs[k] = safe_eval(v)
        except:
            continue
