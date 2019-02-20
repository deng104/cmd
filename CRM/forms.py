from django import forms
from django.core.validators import RegexValidator
from CRM.models import Customer, ConsultRecord, Enrollment, ClassList, CourseRecord, StudyRecord


class BootstrapBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=20,
        label='姓名',
        strip=True,  # 是否移除用户输入空白.
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '用户名最长32位',
        },
        widget=forms.widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '姓名'},)
    )

    password = forms.CharField(
        min_length=8,
        max_length=18,
        label='密码',
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'min_length': '密码最短8位',
            'max_length': '密码最长18位',
        },
        widget=forms.widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'},)
    )

    re_password = forms.CharField(
        label='确认密码',
        error_messages={
            'required': '不能为空',
        },
        widget=forms.widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': '确认密码'},)
    )

    email = forms.CharField(
        label='邮箱',
        error_messages={
            'required': '不能为空',
            'invalid': '请输入正确的邮箱地址',
        },
        widget=forms.widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱'},),
        validators=[RegexValidator(r'[1-9][0-9]{4,12}@qq\.com', '请输入正确的邮箱')]
    )

    mobile = forms.CharField(
        label='手机号',
        error_messages={
            'required': '不能为空',
            'invalid': '前输入正确的手机号',
            'max_length': '手机号最长11位',
        },
        widget=forms.widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '手机号码'},),
        validators = [RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的手机号码')]
    )


'''
class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {'course': forms.widgets.SelectMultiple}
'''


class CustomerForm(BootstrapBaseForm):

    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'course': forms.widgets.SelectMultiple,
            'birthday': forms.widgets.DateInput(attrs={'type': 'date'}),
        }


# 沟通记录的form.
class ConsultRecordForm(forms.ModelForm):

    class Meta:
        model = ConsultRecord
        exclude = ['delete_status', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.instance)
        print('#'*120)
        # 把customer字段的choice设置成我的客户
        # 方法一, 修改字段的choice选项
        # self.fields['customer'].choices = Customer.objects.filter(
        #       consultant=self.initial.consultant).values_list('id', 'name')
        # 方法二, 将form表的字段直接修改
        self.fields['customer'] = forms.models.ModelChoiceField(queryset=Customer.objects.filter(consultant=self.instance.consultant))
        self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        #  修改跟进人跟进人只能是自己
        self.fields['consultant'].choices = [(self.instance.consultant.id, self.instance.consultant.name), ]


# 报名表
class EnrollmentForm(BootstrapBaseForm):
    class Meta:
        model = Enrollment
        exclude = ['contract_approved', 'delete_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  限制添加报名表的时候只能选自己私户
        self.fields['customer'].choices = [(self.instance.customer.id, self.instance.customer.name)]


#  班级表
class ClassListForm(BootstrapBaseForm):
    class Meta:
        model = ClassList
        fields = '__all__'


# 课程记录
class CourseRecordForm(BootstrapBaseForm):
    class Meta:
        model = CourseRecord
        fields = '__all__'


#  学习记录.
class StudyRecordForm(BootstrapBaseForm):
    class Meta:
        model = StudyRecord
        fields = ['student', 'attendance', 'score', 'homework_note']
