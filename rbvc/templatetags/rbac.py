from django import template
from django.conf import settings
import re

register = template.Library()


@register.inclusion_tag(filename='rbac/menu.html')
def show_menu(request):
    # 先从配置文件中找到存放菜单信息的session key是什么
    menu_key = getattr(settings, 'MENU_SESSION_KEY', 'menu_list')
    # 从session中取出菜单信息
    menu_list = request.session[menu_key]
    # 给当前的菜单添加active样式
    for menu in menu_list:
        if re.match(r'^{}$'.format(menu['url']), request.path_info):
            # 当前这个menu需要加一个active样式file: /D:/Qishijihua/CRM/luffy_permission/luffy_permission/web/views/customer.py
            menu['class'] = 'active'
            break
    return {'menu_list': menu_list}
