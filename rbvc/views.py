from django.shortcuts import render, redirect, HttpResponse
from rbvc.models import UserInfo
from rbvc.utils import permission

# Create your views here.


def login(request):
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = UserInfo.objects.filter(username=username, password=password).first()
        if user_obj:
            # 登录成功
            permission.init(request, user_obj)
            return redirect('/customer/list/')
        else:
            error_msg = '用户名或密码错误'
    return render(request, 'login.html', {'error_msg': error_msg})


def logout(request):
    request.session.flush()
    return redirect('/login/')
