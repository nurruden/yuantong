"""
权限相关工具函数模块
提供权限检查、装饰器等功能
"""

import logging
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def user_has_permission(user, permission_code):
    """检查用户是否有指定权限"""
    # 超级管理员直接放行
    if user.is_superuser:
        return True
    
    # 使用新的层级权限检查函数
    try:
        from home.utils import has_hierarchical_permission
        return has_hierarchical_permission(user, permission_code)
    except Exception as e:
        # 如果新函数出错，回退到原有的角色权限检查
        try:
            from system.models import Permission
            return Permission.objects.filter(
                rolepermission__role__userrole__user=user,
                code=permission_code
            ).exists()
        except:
            # 如果system模型不存在，暂时返回True
            return True


def permission_required(permission_code):
    """权限检查装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("未登录")
            # 检查用户是否有该权限
            if not user_has_permission(request.user, permission_code):
                # 渲染美观的403错误页面
                context = {
                    'user': request.user,
                    'request_path': request.path,
                    'permission_code': permission_code
                }
                return render(request, '403.html', context, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def has_system_settings_permission(userid):
    """检查用户是否有系统设置权限"""
    from home.models import MenuPermission
    
    try:
        # 查询数据库中的权限配置
        permission = MenuPermission.objects.filter(
            menu_name='系统设置',
            is_active=True
        ).first()
        
        if permission:
            # 如果有权限配置，检查用户是否在允许列表中
            allowed_users = permission.allowed_users.split(',') if permission.allowed_users else []
            allowed_users = [user.strip() for user in allowed_users if user.strip()]
            return userid in allowed_users
        else:
            # 如果没有权限配置，则使用默认的管理员用户
            default_allowed_users = ['GaoBieKeLe', 'yanyanzhao']
            return userid in default_allowed_users
    except Exception as e:
        # 如果数据库查询出错，回退到默认权限
        logger.warning(f"权限检查出错: {e}")
        default_allowed_users = ['GaoBieKeLe', 'yanyanzhao']
        return userid in default_allowed_users


def system_settings_required(view_func):
    """系统设置权限检查装饰器"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not has_system_settings_permission(request.user.username):
            raise PermissionDenied("您没有权限访问系统设置功能")

        return view_func(request, *args, **kwargs)

    return wrapper


def filter_menu_by_permission(menu_items, userid):
    """根据用户权限过滤菜单项"""
    # 暂时移除权限检查，显示所有菜单项
    return menu_items
