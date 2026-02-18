#!/usr/bin/env python
"""
RBAC数据初始化脚本
用于创建测试角色、权限和用户角色分配数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from django.contrib.auth.models import User
from system.models import Role, Permission, UserRole

def create_test_roles():
    """创建测试角色"""
    roles_data = [
        {'name': '管理员', 'description': '系统管理员，拥有所有权限'},
        {'name': '操作员', 'description': '普通操作员，拥有基本操作权限'},
        {'name': '查看者', 'description': '只读用户，只能查看数据'},
        {'name': '审核员', 'description': '数据审核员，负责审核数据'},
    ]
    
    created_roles = []
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        if created:
            print(f"创建角色: {role.name}")
        else:
            print(f"角色已存在: {role.name}")
        created_roles.append(role)
    
    return created_roles

def create_test_permissions():
    """创建测试权限"""
    permissions_data = [
        {'code': 'user_management', 'name': '用户管理', 'permission_type': 'admin', 'module': 'system', 'description': '用户管理权限'},
        {'code': 'role_management', 'name': '角色管理', 'permission_type': 'admin', 'module': 'system', 'description': '角色管理权限'},
        {'code': 'permission_management', 'name': '权限管理', 'permission_type': 'admin', 'module': 'system', 'description': '权限管理权限'},
        {'code': 'qc_report_view', 'name': 'QC报表查看', 'permission_type': 'view', 'module': 'production', 'description': '查看QC报表'},
        {'code': 'qc_report_edit', 'name': 'QC报表编辑', 'permission_type': 'edit', 'module': 'production', 'description': '编辑QC报表'},
        {'code': 'qc_report_delete', 'name': 'QC报表删除', 'permission_type': 'delete', 'module': 'production', 'description': '删除QC报表'},
        {'code': 'production_view', 'name': '生产数据查看', 'permission_type': 'view', 'module': 'production', 'description': '查看生产数据'},
        {'code': 'production_edit', 'name': '生产数据编辑', 'permission_type': 'edit', 'module': 'production', 'description': '编辑生产数据'},
        {'code': 'system_settings', 'name': '系统设置', 'permission_type': 'admin', 'module': 'system', 'description': '系统设置权限'},
    ]
    
    created_permissions = []
    for perm_data in permissions_data:
        permission, created = Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'permission_type': perm_data['permission_type'],
                'module': perm_data['module'],
                'description': perm_data['description']
            }
        )
        if created:
            print(f"创建权限: {permission.name}")
        else:
            print(f"权限已存在: {permission.name}")
        created_permissions.append(permission)
    
    return created_permissions

def create_test_user_roles():
    """创建测试用户角色分配"""
    # 获取或创建测试用户
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': '系统',
            'last_name': '管理员',
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"创建管理员用户: {admin_user.username}")
    
    # 获取角色
    admin_role = Role.objects.filter(name='管理员').first()
    operator_role = Role.objects.filter(name='操作员').first()
    viewer_role = Role.objects.filter(name='查看者').first()
    
    if not admin_role:
        print("错误: 管理员角色不存在")
        return
    
    # 为管理员用户分配管理员角色
    user_role, created = UserRole.objects.get_or_create(
        user=admin_user,
        role=admin_role
    )
    if created:
        print(f"为用户 {admin_user.username} 分配角色 {admin_role.name}")
    else:
        print(f"用户角色分配已存在: {admin_user.username} -> {admin_role.name}")
    
    # 如果有其他用户，也可以为他们分配角色
    other_users = User.objects.exclude(username='admin')[:3]
    roles = [operator_role, viewer_role]
    
    for i, user in enumerate(other_users):
        if i < len(roles) and roles[i]:
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=roles[i]
            )
            if created:
                print(f"为用户 {user.username} 分配角色 {roles[i].name}")
            else:
                print(f"用户角色分配已存在: {user.username} -> {roles[i].name}")

def main():
    """主函数"""
    print("开始初始化RBAC测试数据...")
    
    try:
        # 创建测试角色
        print("\n1. 创建测试角色...")
        roles = create_test_roles()
        
        # 创建测试权限
        print("\n2. 创建测试权限...")
        permissions = create_test_permissions()
        
        # 创建测试用户角色分配
        print("\n3. 创建测试用户角色分配...")
        create_test_user_roles()
        
        print("\n✅ RBAC测试数据初始化完成！")
        print(f"创建了 {len(roles)} 个角色")
        print(f"创建了 {len(permissions)} 个权限")
        
        # 显示统计信息
        print(f"\n当前数据统计:")
        print(f"- 角色总数: {Role.objects.count()}")
        print(f"- 权限总数: {Permission.objects.count()}")
        print(f"- 用户角色分配总数: {UserRole.objects.count()}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 