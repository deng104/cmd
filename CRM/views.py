from django.shortcuts import render, redirect, HttpResponse
from django import views
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile, Customer, ConsultRecord, Enrollment, PaymentRecord
from CRM.forms import RegisterForm, CustomerForm, ConsultRecordForm, EnrollmentForm
from django.urls import reverse
from django.http import JsonResponse, QueryDict
from utils.mypage import Pagination
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from rbvc.utils import permission


class LoginView(views.View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        is_check = (request.POST.get('is_check', None) == '777')
        user_obj = auth.authenticate(request, email=username, password=password)
        if user_obj:
            auth.login(request, user_obj)
            permission.init(request, user_obj)
            if is_check:
                request.session.set_expiry(7*24*60*60)
            else:
                request.session.set_expiry(0)
            return redirect(reverse('customer_list'))
        else:
            return render(request, 'login.html', {'error_msg': '邮箱或密码错误'})


# 两个登录界面.都配置有样式.想用哪个用哪个.
def login2(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        is_check = (request.POST.get('is_check', None) == '777')
        user_obj = auth.authenticate(request, email=username, password=password)
        print(user_obj)
        if user_obj:
            auth.login(request, user_obj)
            if is_check:
                request.session.set_expiry(7*24*60*60)
            else:
                request.session.set_expiry(0)
            return redirect('customer_list')
        else:
            return render(request, 'login2.html', {'error_msg': '邮箱或密码错误'})

    return render(request, 'login2.html')


@login_required
def index(request):
    return render(request, 'index.html')


def reg(request):
    obj = RegisterForm()
    if request.method == 'POST':
        obj = RegisterForm(request.POST)
        if obj.is_valid():
            print(obj.cleaned_data)
            obj.cleaned_data.pop('re_password')
            auth_obj = UserProfile.objects.create_user(**obj.cleaned_data)
            return redirect('/login/')
    return render(request, 'reg.html', {'form_obj': obj})



# ajax检查邮箱是否存在
def check_email(request):
    email = request.POST.get('email')
    ret = {'code': 0}
    obj = UserProfile.objects.filter(email=email)
    if obj:
        ret['code'] = 1
        ret['error_msg'] = '邮箱已存在'
        print(ret)
    return JsonResponse(ret)


def register(request):
    if request.method == 'POST':
        email = request.POST.get('userEmail', None)
        if email:
            password = request.POST.get('userPassword', 123)
            re_password = request.POST.get('userRePassword', 321)
            mobile = request.POST.get('userPhone', None)
            name = request.POST.get('username', None)
            if password == re_password:
                UserProfile.objects.create_superuser(name=name, email=email, password=password, mobile=mobile, )
                return redirect('/login2/')
        else:
            error_msg = '两次密码不一致'
            return render(request, 'register.html', {'error_msg': error_msg})
    return render(request, 'register.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/login/')


class CustomerListView(views.View):
    @method_decorator(login_required)
    def get(self, request):
        url_prefix = request.path_info
        qd = request.GET.copy()  # <QueryDict: {'query': ['了']}>
        # qd._mutable = True  # 让QueryDict对象可修改
        current_page = request.GET.get('page', 1)
        if request.path_info == reverse('my_customer'):
            # 获取私户信息
            query_set = Customer.objects.filter(consultant=request.user)  # request.user-->当前登录的人
        else:
            # 获取所有公户信息
            query_set = Customer.objects.filter(consultant__isnull=True)
        # 根据模糊检索的条件对query_set再做过滤.
        # 找到name, qq, qq_name字段包含query_value的哪些数据就是搜索的结果
        q = self._get_query_q(['name', 'qq', 'qq_name'])
        query_set = query_set.filter(q)
        page_obj = Pagination(current_page, query_set.count(), url_prefix, qd, per_page=3)
        data = query_set[page_obj.start:page_obj.end]
        # 2.0 返回之前的页面
        # 2.1 获取当前请求的带query参数的URL
        url = request.get_full_path()
        # 2.2 生成一个空的QueryDict对象
        query_params = QueryDict(mutable=True)
        # 2.3 添加一个next键值对
        query_params['next'] = url
        # 2.4 利用QueryDict内置方法编码成URL
        next_url = query_params.urlencode()
        # 在页面上展示出来
        return render(request, 'customer_list.html', {'customer_list': data, 'next_url': next_url, 'page_html': page_obj.page_html()})

    @method_decorator(login_required)
    def post(self, request):
        #  批量操作(变公户, 变私户)
        cid = request.POST.getlist('cid')
        action = request.POST.get('action')
        # 判断self是否有一个_action的方法, 如果有就执行, 否则就回复404
        if not hasattr(self, '_{}'.format(action)):
            return HttpResponse('404页面')
        ret = getattr(self, '_{}'.format(action))(cid)
        if ret:
            return ret
        return redirect(reverse('customer_list'))

    def _to_private(self, cid):
        update_num = len(cid)
        # 判断 我们已经有的私户数量 + 这一次要提交的 < 我的私户限制
        valid_num = (self.request.user.customers.count() + update_num) - settings.CUSTOMER_NUM_LIMIT
        if valid_num > 0:
            return HttpResponse('做人要厚道, 给别人留点机会, 做多只能再添加{}个!'.format(
                settings.CUSTOMER_NUM_LIMIT - self.request.user.customers.count()
            ))
        # 考虑到多个销售争抢同一个客户的情况
        with transaction.atomic():
            select_objs = Customer.objects.filter(id__in=cid, consultant__isnull=True).select_for_update()
            select_num = select_objs.count()
            print(select_objs, '===========', select_num)
            if select_num != update_num:
                return HttpResponse('手太慢了, 已经被别人抢走了')
            else:
                select_objs.update(consultant=self.request.user)

    def _to_public(self, cid):
        #  方法一, 找到所有要操作的客户数据, 把他们的销售字段设置为空
        Customer.objects.filter(id__in=cid).update(consultant=None)
        #  方法二, 从我的列表里面把指定客户删除掉
        # request.user.customers.remove(*Customer.objects.filter(id__in=cid))

    def _get_query_q(self, field_list, op='OR'):
        #  从URL中取到query参数
        query_value = self.request.GET.get('query', '')
        q = Q()
        #  指定Q查询内部的操作是OR还是AND
        q.connector = op
        #  遍历要检索的字段, 挨个添加子Q对象
        for field in field_list:
            q.children.append(Q(('{}__icontains'.format(field), query_value)))
        return q



# 新增和编辑二合一的视图函数
@login_required
def customer(request, edit_id=None):
    # 如果edit_id= None表示是新增操作
    # 如果edit_id有值表示是编辑操作
    customer_obj = Customer.objects.filter(pk=edit_id).first()
    form_obj = CustomerForm(instance=customer_obj)
    if request.method == 'POST':
        # 使用POST提交得数据去更新指定得instance实例
        form_obj = CustomerForm(request.POST, instance=customer_obj)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next', reverse('customer_list'))
            return redirect(next_url)
    return render(request, 'customer.html', {'form_obj': form_obj, 'edit_id': edit_id})


# 展示沟通记录
@login_required
def consult_record_list(request, cid=0):
    if int(cid) == 0:
        query_set = ConsultRecord.objects.filter(consultant=request.user, delete_status=False)
    else:
        query_set = ConsultRecord.objects.filter(customer_id=cid, delete_status=False)
    return render(request, 'consult_record_list.html', {'consult_record': query_set})


# 添加和编辑沟通记录
def consult_record(request, edit_id=None):
    record_obj = ConsultRecord.objects.filter(id=edit_id).first()
    if not record_obj:  # 没有数据说明是添加
        record_obj = ConsultRecord(consultant=request.user)  # 生成一个销售是我的ConsultRecord对象
    form_obj = ConsultRecordForm(instance=record_obj, initial={'consultant': request.user})
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=record_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record_list', kwargs={'cid': 0}))
    return render(request, 'consult_record.html', {'form_obj': form_obj, 'edit_id': edit_id})


#  报名表
class EnrollmentListView(views.View):
    def get(self, request, customer_id=0):
        if int(customer_id) == 0:
            # query_set = Enrollment.objects.filter(customer__consultant=request.user)
            query_set = Enrollment.objects.filter(customer__consultant=request.user)
        else:
            query_set = Enrollment.objects.filter(customer_id=customer_id)
        return render(request, 'enrollment_list.html', {'enrollment_list': query_set})


# 添加和编辑报名记录
def enrollment(request, customer_id=None, enrollment_id=None):
    # 先根据报名表id去查询
    enrollment_obj = Enrollment.objects.filter(id=enrollment_id).first()
    #  查询不到报名表说明是新增报名表, 又因为是新增报名表必须指定客户
    if not enrollment_obj:
        enrollment_obj = Enrollment(customer=Customer.objects.filter(id=customer_id).first())
    form_obj = EnrollmentForm(instance=enrollment_obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=enrollment_obj)
        if form_obj.is_valid():
            new_obj = form_obj.save()
            # 报名成功, 更改客户当前的状态
            new_obj.customer.status = 'signed'
            new_obj.customer.save()  # 改的那张表的字段就保存那个对象
            return redirect(reverse('enrollment_list', kwargs={'customer_id': 0}))
        else:
            return HttpResponse('出错啦!')
    return render(request, 'enrollment.html', {'form_obj': form_obj})


# 缴费记录
class PaymentRecordView(views.View):
    def get(self, request):
        query_set = PaymentRecord.objects.filter()
