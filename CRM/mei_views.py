#  班主任相关的视图都放在这里
from django import views
from django.shortcuts import render, redirect, HttpResponse
from CRM.models import ClassList, CourseRecord, StudyRecord
from CRM.forms import ClassListForm, CourseRecordForm, StudyRecordForm
from django.urls import reverse
from django.http import QueryDict


class ClassListView(views.View):
    def get(self, request):
        query_set = ClassList.objects.all()
        return render(request, 'class_list.html', {'class_list': query_set})


#  新增和编辑班级
def op_class(request, edit_id=None):
    edit_obj = ClassList.objects.filter(id=edit_id).first()
    form_obj = ClassListForm(instance=edit_obj)
    if request.method == 'POST':
        form_obj = ClassListForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('class_list'))
    return render(request, 'op_class.html', {'form_obj': form_obj, 'edit_id': edit_id})


# 课程记录
class CourseListView(views.View):
    def get(self, request, class_id):
        query_set = CourseRecord.objects.filter(re_class_id=class_id)
        current_url = request.get_full_path()
        qd = QueryDict(mutable=True)
        qd['next'] = current_url
        return render(request, 'course_list.html', {'course_record_list': query_set, 'next_url': qd.urlencode(), 'class_id': class_id})

    def post(self, request, class_id):
        #  从POST提交过来的数据里找action和勾选的课程记录id
        cid = request.POST.getlist('cid')
        action = request.POST.get('action')
        # 利用反射执行指定的动作
        if hasattr(self, '_{}'.format(action)):
            ret = getattr(self, '_{}'.format(action))(cid)
        else:
            return HttpResponse('滚')
        if ret:
            return ret
        else:
            return redirect(redirect('course_record_list', kwargs={'class_id': class_id}))

    def _multi_init(self, cid):
        courser_objs = CourseRecord.objects.filter(id__in=cid)
        for course_record in courser_objs:
            all_student = course_record.re_class.customer_set.all()
            studentreord_objs = (StudyRecord(course_record=course_record, student=student) for student in all_student )
            StudyRecord.objects.bulk_create(studentreord_objs)
        return HttpResponse('初始化好了')


def course_record(request, class_id=None, course_record_id=None):
    class_obj = ClassList.objects.filter(id=class_id).first()
    edit_obj = CourseRecord.objects.filter(id=course_record_id).first()
    form_obj = CourseRecordForm(instance=edit_obj, initial={'re_class': class_obj})
    if request.method == 'POST':
        form_obj = CourseRecordForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next', '/CRM/class_list')
            return redirect(next_url)
    return render(request, 'course_record.html', {'form_obj': form_obj, 'edit_id': course_record_id})


from django.forms import modelformset_factory


# 学习记录列表
def study_record_list(request, course_record_id):
    FormSet = modelformset_factory(StudyRecord, StudyRecordForm, extra=0)

    query_set = StudyRecord.objects.filter(course_record_id=course_record_id)
    formset_obj = FormSet(queryset=query_set)
    if request.method == 'POST':
        formset_obj = FormSet(request.POST, queryset=query_set)
        if formset_obj.is_valid():
            formset_obj.save()
    return render(request, 'study_record_list.html', {'formset_obj': formset_obj})
