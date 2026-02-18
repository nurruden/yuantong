"""
URL configuration for yuantong project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from wechat_auth.views import wechat_login, WeChatCallbackView, custom_logout, WeChatMessageReceiveView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# 添加微信验证文件处理视图
@csrf_exempt
def wechat_verify(request):
    return HttpResponse("fRjacNzI3msWh1Wf", content_type='text/plain')

urlpatterns = [
    path('WW_verify_fRjacNzI3msWh1Wf.txt', wechat_verify, name='wechat_verify'),
    # 企业微信消息接收URL必须在include('home.urls')之前，避免被其他路由拦截
    path('wechat/message/receive/', WeChatMessageReceiveView.as_view(), name='wechat_message_receive'),
    path('wechat/callback/', WeChatCallbackView.as_view(), name='wechat_callback'),
    path('wechat/login/', wechat_login, name='wechat_login'),
    path('login/', wechat_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('tasks/', include('tasks.urls')),  # 任务管理
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # 将根路径直接指向home视图（放在最后，避免拦截其他路由）
]
