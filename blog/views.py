from django.shortcuts import get_object_or_404, render
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from .models import Blog, BlogType
from read_statistics.untils import read_statistics_once_read
from django.db.models import Count
from django.conf import settings


# Create your views here.

# 公共
def get_blog_list_common_date(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, 6)
    # 获取url的页面参数(GET请求)
    page_num = request.GET.get('page', 1)
    # 这里也会处理输入错误的信息,默认调到第一页
    page_of_blogs = paginator.get_page(page_num)

    # 获取当前页码
    current_page_num = page_of_blogs.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    # 如果在第一位的数字大于等于2,那么插入...
    if page_range[0] - 1 >=2:
        page_range.insert(0, "...")
    # 如果当前显示最后一位的数字小于等于实际存在的list2位
    if paginator.num_pages - page_range[-1] >=2:
        page_range.append("...")
    
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取所有分类及分类中文章总数
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)


    # 获取所有日期及日期中文章总数
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count
    
    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = blog_types_list
    context['blog_dates'] = blog_dates_dict
    return context

# 列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    # 每10页进行分页
    context = get_blog_list_common_date(request, blogs_all_list)
    return render(request, 'blog/blog_list.html', context)
    
# 分类
def blogs_with_type(request, blog_type_pk):
    
    # 在get_object_or_404方法中第一个参数是model对象,也就是创建的模型,第二个是查询条件pk=id 也是主键
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk) # 所以这句的意思就是:在BlogType这个模型中查找id=传入参数的对象,没有则抛出404错误
    
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_type'] = blog_type # 这里是将获取到的对象使用键值对封装起来
    return render(request, 'blog/blogs_with_type.html', context) # 这里是将context参数传入blogs_with_type.html中

# 类型
def blogs_with_type_name(request):
    # context = {}
    # blog_type = Blog.objects.filter(blog_type=Blog.blog_type)
    # context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type_name.html', )

# 日期
def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month, )
    context = get_blog_list_common_date(request, blogs_all_list)
    return render(request, 'blog/blog_with_date.html', context) # 这里是将context参数传入blogs_with_type.html中

# 内容
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    
    
    context = {}
    context['previous_blogs'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render(request, 'blog/blog_detail.html', context)
    # 这里是设置进入detail页面时,增加一个cookie
    response.set_cookie(read_cookie_key, 'true') # 响应，设置cookie在离开时才会失效
    return response