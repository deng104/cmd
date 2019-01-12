from django.conf.urls import url
from CRM import views, mei_views

urlpatterns = [
    url(r'customer_list/$', views.CustomerListView.as_view(), name='customer_list'),  # 所有客户列表
    url(r'my_customer/$', views.CustomerListView.as_view(), name='my_customer'),  # 我的客户列表
    url(r'add/$', views.customer, name='add_customer'),
    url(r'edit_customer/(\d+)/$', views.customer, name='edit_customer'),
    url(r'customer/(\d+)/$', views.customer, name='customer'),
    # ============================================================
    #  沟通记录
    url(r'consult_record_list/(?P<cid>\d+)$', views.consult_record_list, name='consult_record_list'),
    url(r'add_consult_record/$', views.consult_record, name='add_consult_record'),
    url(r'edit_consult_record/(\d+)$', views.consult_record, name='edit_consult_record'),
    #  报名表
    url(r'enrollment_list/(?P<customer_id>\d+)/$', views.EnrollmentListView.as_view(), name='enrollment_list'),
    url(r'add_enrollment/(?P<customer_id>\d+)/$', views.enrollment, name='add_enrollment'),
    url(r'edit_enrollment/(?P<enrollment_id>\d+)/$', views.enrollment, name='edit_enrollment'),
    # 班级管理
    url(r'^class_list/$', mei_views.ClassListView.as_view(), name='class_list'),
    url(r'^add_class/$', mei_views.op_class, name='add_class'),
    url(r'^edit_class/(\d+)/$', mei_views.op_class, name='edit_class'),
    # 课程记录
    url(r'^course_record_list/(?P<class_id>\d+)/$', mei_views.CourseListView.as_view(), name='course_record_list'),
    url(r'^add_course_record/(?P<class_id>\d+)/$', mei_views.course_record, name='add_course_record'),
    url(r'^edit_course_record/(?P<course_record_id>\d+)/$', mei_views.course_record, name='edit_course_record'),
    #  学习记录
    url(r'^study_record_list/(?P<course_record_id>\d+)/$', mei_views.study_record_list, name='study_record_list'),
    #  缴费记录
    url(r'^payment_record_list/$', views.PaymentRecordView.as_view(), name='payment_record_list'),


]