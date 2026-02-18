#!/usr/bin/env python
"""
添加系统设置权限脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from home.models import MenuPermission
from django.contrib.auth.models import User

def add_system_permission():
    """添加系统设置权限"""
    
    print("=== 系统设置权限管理 ===")
    
    # 获取所有用户
    users = User.objects.all()
    print(f"\n当前系统用户 ({users.count()} 个):")
    for i, user in enumerate(users, 1):
        print(f"{i:2d}. {user.username} ({user.first_name} {user.last_name})")
    
    # 获取当前权限配置
    try:
        permission = MenuPermission.objects.filter(
            menu_name='系统设置',
            is_active=True
        ).first()
        
        if permission:
            current_users = permission.allowed_users.split(',') if permission.allowed_users else []
            current_users = [user.strip() for user in current_users if user.strip()]
            print(f"\n当前有系统设置权限的用户: {', '.join(current_users)}")
        else:
            print("\n当前没有系统设置权限配置")
            current_users = []
    except Exception as e:
        print(f"获取权限配置出错: {e}")
        current_users = []
    
    # 选择要添加权限的用户
    print("\n请选择要添加系统设置权限的用户:")
    print("输入用户编号（多个用户用逗号分隔，如: 1,3,5）")
    print("输入 'all' 给所有用户添加权限")
    print("输入 'admin' 只给管理员用户添加权限")
    print("输入 'cancel' 取消操作")
    
    choice = input("\n请输入选择: ").strip()
    
    if choice.lower() == 'cancel':
        print("操作已取消")
        return
    
    # 确定要添加权限的用户
    users_to_add = []
    
    if choice.lower() == 'all':
        users_to_add = [user.username for user in users]
    elif choice.lower() == 'admin':
        users_to_add = [user.username for user in users if user.is_superuser or user.is_staff]
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            for idx in indices:
                if 0 <= idx < len(users):
                    users_to_add.append(users[idx].username)
        except ValueError:
            print("输入格式错误")
            return
    
    if not users_to_add:
        print("没有选择任何用户")
        return
    
    # 合并现有用户和新用户
    all_users = list(set(current_users + users_to_add))
    
    # 更新权限配置
    try:
        MenuPermission.objects.update_or_create(
            menu_name='系统设置',
            defaults={
                'allowed_users': ','.join(all_users),
                'is_active': True
            }
        )
        
        print(f"\n✅ 权限更新成功！")
        print(f"现在有系统设置权限的用户: {', '.join(all_users)}")
        print(f"\n新增用户: {', '.join(users_to_add)}")
        
    except Exception as e:
        print(f"❌ 权限更新失败: {e}")

def remove_system_permission():
    """移除系统设置权限"""
    
    print("=== 移除系统设置权限 ===")
    
    try:
        permission = MenuPermission.objects.filter(
            menu_name='系统设置',
            is_active=True
        ).first()
        
        if not permission:
            print("当前没有系统设置权限配置")
            return
        
        current_users = permission.allowed_users.split(',') if permission.allowed_users else []
        current_users = [user.strip() for user in current_users if user.strip()]
        
        print(f"当前有系统设置权限的用户: {', '.join(current_users)}")
        
        if not current_users:
            print("没有用户有系统设置权限")
            return
        
        print("\n请选择要移除权限的用户:")
        print("输入用户名（多个用户用逗号分隔）")
        print("输入 'all' 移除所有用户的权限")
        print("输入 'cancel' 取消操作")
        
        choice = input("\n请输入选择: ").strip()
        
        if choice.lower() == 'cancel':
            print("操作已取消")
            return
        
        if choice.lower() == 'all':
            users_to_remove = current_users
        else:
            users_to_remove = [user.strip() for user in choice.split(',')]
        
        # 移除用户权限
        remaining_users = [user for user in current_users if user not in users_to_remove]
        
        if remaining_users:
            permission.allowed_users = ','.join(remaining_users)
            permission.save()
            print(f"\n✅ 权限移除成功！")
            print(f"剩余有权限的用户: {', '.join(remaining_users)}")
        else:
            # 如果没有剩余用户，删除权限配置
            permission.delete()
            print("\n✅ 已移除所有用户的系统设置权限")
        
    except Exception as e:
        print(f"❌ 权限移除失败: {e}")

def show_current_permissions():
    """显示当前权限配置"""
    
    print("=== 当前权限配置 ===")
    
    try:
        permissions = MenuPermission.objects.filter(is_active=True)
        
        if not permissions.exists():
            print("当前没有权限配置")
            return
        
        for perm in permissions:
            users = perm.allowed_users.split(',') if perm.allowed_users else []
            users = [user.strip() for user in users if user.strip()]
            print(f"\n{perm.menu_name}:")
            print(f"  用户: {', '.join(users) if users else '无'}")
            print(f"  状态: {'激活' if perm.is_active else '禁用'}")
            
    except Exception as e:
        print(f"获取权限配置出错: {e}")

def main():
    """主函数"""
    
    print("系统设置权限管理工具")
    print("=" * 30)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示当前权限配置")
        print("2. 添加系统设置权限")
        print("3. 移除系统设置权限")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            show_current_permissions()
        elif choice == '2':
            add_system_permission()
        elif choice == '3':
            remove_system_permission()
        elif choice == '4':
            print("退出程序")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == '__main__':
    main()
