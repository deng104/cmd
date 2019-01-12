from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from django.conf import settings
import re


class RBACMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 获取当前请求的URL
        current_url = request.path_info
        # 判断当前访问的URL在不在白名单中
        for url in getattr(settings, 'WHITE_URLS', []):
            if re.match(r'^{}$'.format(url), current_url):
                # 如果是白名单的URL直接放行
                return
            # 判断当前访问的URL在不在白名
        key = getattr(settings, 'PERMISSION_SESSION_KEY', 'permission_list')
        permission_list = request.session.get(key, [])
        for pattern in permission_list:
            if re.match('^{}$'.format(pattern), current_url):
                return None
        else:
            return HttpResponse('没有权限')
