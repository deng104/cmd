"""
RBAC组件
权限相关的模块
"""
from django.conf import settings


def init(request, user_obj):
    """
    根据当前登录的用户初始化权限信息和菜单信息, 保存到session中
    :param request: 请求对象
    :param user_obj: 登录的用户对象
    :return:
    """
    # 登陆成功, 将当前用户的权限信息查询出来
    queryset = user_obj.roles.all().filter(permissions__isnull=False).values(
        'permissions__url',
        'permissions__title',
        'permissions__is_menu',
        'permissions__icon',
    ).distinct()
    # 先取到权限列表
    permission_list = []
    # 存放菜单信息的列表
    menu_list = []
    for i in queryset:
        permission_list.append(i['permissions__url'])  # 能够访问的权限列表
        # 再取出菜单列表
        if i.get('permissions__is_menu'):
            menu_list.append({
                'url': i['permissions__url'],  # 菜单的URL
                'title': i['permissions__title'],  # 菜单的标题
                'icon': i['permissions__icon']  # 菜单的图表样式
            })

    # 将权限信息保存到session数据中
    permission_key = getattr(settings, 'PERMISSION_SESSION_KEY', 'permission_list')
    menu_key = getattr(settings, 'MENU_SESSION_KEY', 'menu_list')
    request.session[permission_key] = permission_list
    # 存菜单信息到session数据中
    request.session[menu_key] = menu_list
