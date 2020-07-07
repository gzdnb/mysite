import datetime
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from django.shortcuts import render_to_response, render, redirect
from read_statistics.untils import get_senve_days_read_date, get_today_hot_read_date, get_yestoday_hot_read_date
from django.contrib.contenttypes.models import ContentType
from django.contrib import auth
from blog.models import Blog
from django.urls import reverse
from .forms import LoginForm, RegForm
from django.contrib.auth.models import User


def get_7_day_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date).values('id', 'title').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
    return blogs[:3]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_senve_days_read_date(blog_content_type)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    return render(request, 'home.html', context)

def chart(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_senve_days_read_date(blog_content_type)
    today_hot_read = get_today_hot_read_date(blog_content_type)
    yestoday_hot_read = get_yestoday_hot_read_date(blog_content_type)
    # senvenday_hot_read = get_7_day_hot_blogs()

    # 获取7天热门博客的缓存数据
    hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
    if hot_blogs_for_7_days is None:
        hot_blogs_for_7_days = get_7_day_hot_blogs()
        cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600)
        print("not use cache")
    else:
        print("use cache")


    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_read'] = today_hot_read
    context['yestoday_hot_read'] = yestoday_hot_read
    context['senvenday_hot_read'] = hot_blogs_for_7_days
    return render(request, 'chart.html', context)

def login(request):
    # username = request.POST.get('username', '')
    # password = request.POST.get('password', '')
    # user = auth.authenticate(request, username=username, password=password)
    # referer = request.META.get('HTTP_REFERER', reverse('home'))
    # # 检测有没有登录用户,如果没有那么提示登录,登陆成功并转到评论页面
    # if user is not None:
    #     auth.login(request, user)
    #     return redirect(referer)
    # else:
    #     return render(request, 'error.html', {'message':'用户名或密码不正确'})

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))                     
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        # 创建用户
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)
            user.save() 

            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))                
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
    context = {}
    return render(request, 'user_info.html', context)
