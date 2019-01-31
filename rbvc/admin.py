from django.contrib import admin
from rbvc.models import Permission, Role


class PermissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'is_menu', 'icon']  # 控制admin页面显示哪些字段
    list_editable = ['url', 'is_menu', 'icon']  # 可以直接在admin页面编辑的字段


admin.site.register(Permission, PermissionAdmin)
admin.site.register(Role)
