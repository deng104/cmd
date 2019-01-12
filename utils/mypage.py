"""
自定义分页组件
可以返回分页的数据和分页的HTML代码
"""
from django.http import QueryDict


class Pagination(object):

    def __init__(self, current_page, total_count, url_prefix, query_dict=QueryDict(mutable=True), per_page=10, show_page=9):
        """
        初始化分分页器
        :param url_prefix: a标签的URL前缀
        :param query_dict: 空的QueryDict()对象，并且是可修改的
        :param current_page: 当前页码数
        :param total_count: 数据总数
        :param per_page: 每一页显示多少数据， 默认值是10
        :param show_page: 页面显示的页码数， 默认值是9
        """
        # 0.分页的URL前缀
        self.url_prefix = url_prefix
        self.query_dict = query_dict
        # 1. 每一页显示10条数据
        assert per_page > 0  # 每页显示多少的数据必须是一个大于0的数
        self.per_page = per_page
        # 2. 计算需要多少页
        total_page, more = divmod(total_count, per_page)
        if more:
            total_page += 1
        self.total_page = total_page
        # 3. 当前页码
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        current_page = total_page if current_page > total_page else current_page
        # 页码必须是大于0的数
        if current_page < 1:
            current_page = 1
        self.current_page = current_page
        # 4. 页面最多显示的页码数
        self.show_page = show_page
        # 5. 最多显示页码的一半
        self.half_show_page = self.show_page // 2

    @property
    def start(self):
        # 数据切片的开始位置
        return self.per_page * (self.current_page - 1)

    @property
    def end(self):
        # 数据切片的结束为止
        return self.current_page * self.per_page

    # 定义一个返回HTML代码的方法
    def page_html(self):
        if self.total_page == 0:
            return ''
        # 如果总页码数小于最大要显示的页码数
        if self.total_page < self.show_page:
            show_page_start = 1
            show_page_end = self.total_page
        # 左边越界
        elif self.current_page - self.half_show_page < 1:
            show_page_start = 1
            show_page_end = self.show_page
        # 右边越界
        elif self.current_page + self.half_show_page > self.total_page:
            show_page_end = self.total_page
            show_page_start = self.total_page - self.show_page + 1
        else:
            show_page_start = self.current_page - self.half_show_page
            # 页面显示页码的结束
            show_page_end = self.current_page + self.half_show_page
        # 生成分页的HTML代码
        page_list = []
        # 添加分页代码的前缀
        page_list.append('<nav aria-label="Page navigation"><ul class="pagination">')
        # 添加首页
        self.query_dict['page'] = 1
        page_list.append('<li><a href="{}?{}">首页</a></li>'.format(self.url_prefix, self.query_dict.urlencode()))
        # 添加上一
        if self.current_page - 1 < 1:  # 已经到头啦，不让点上一页啦
            page_list.append(
                '<li class="disabled"><a href="" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>')
        else:
            self.query_dict['page'] = self.current_page - 1
            page_list.append(
                '<li><a href="{}?{}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
                    self.url_prefix,
                    self.query_dict.urlencode())
            )
        for i in range(show_page_start, show_page_end + 1):
            self.query_dict['page'] = i
            if i == self.current_page:
                s = '<li class="active"><a href="{1}?{2}">{0}</a></li>'.format(i, self.url_prefix, self.query_dict.urlencode())
            else:
                s = '<li><a href="{1}?{2}">{0}</a></li>'.format(i, self.url_prefix, self.query_dict.urlencode())
            page_list.append(s)
        # 添加下一页
        if self.current_page + 1 > self.total_page:
            page_list.append(
                '<li class="disabled"><a href="" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>')
        else:
            self.query_dict['page'] = self.current_page + 1
            page_list.append(
                '<li><a href="{}?{}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(
                    self.url_prefix,
                    self.query_dict.urlencode())
            )
        # 添加尾页
        self.query_dict['page'] = self.total_page
        page_list.append('<li><a href="{}?{}">尾页</a></li>'.format(self.url_prefix, self.query_dict.urlencode()))
        # 添加分页代码的后缀
        page_list.append('</ul></nav>')
        page_html = ''.join(page_list)
        return page_html
