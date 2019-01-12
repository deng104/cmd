from django.db import models
from CRM.models import UserProfile

# Create your models here.


# 权限表
class Permission(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(max_length=32)
    is_menu = models.BooleanField(default=False)  # 是否能做菜单
    icon = models.CharField(max_length=24, null=True, blank=True)  # 菜单的图标

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = verbose_name


# 角色表
class Role(models.Model):
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField(to='Permission', null=True, blank=True)
    # 把角色表关联用户表
    user = models.ManyToManyField(to=UserProfile, related_name='roles')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

