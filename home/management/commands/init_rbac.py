from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from system.models import Role, Permission, UserRole, RolePermission

class Command(BaseCommand):
    help = '初始化RBAC权限系统，创建默认角色和权限'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化RBAC权限系统...')
        
        # 创建默认角色
        roles = self.create_default_roles()
        
        # 创建默认权限
        permissions = self.create_default_permissions()
        
        # 为角色分配权限
        self.assign_permissions_to_roles(roles, permissions)
        
        # 为现有用户分配默认角色
        self.assign_default_roles_to_users()
        
        self.stdout.write(self.style.SUCCESS('RBAC权限系统初始化完成！'))

    def create_default_roles(self):
        """创建默认角色"""
        roles = {}
        
        # 超级管理员角色
        admin_role, created = Role.objects.get_or_create(
            name='超级管理员',
            defaults={'description': '拥有系统所有权限的管理员角色'}
        )
        roles['admin'] = admin_role
        if created:
            self.stdout.write(f'创建角色: {admin_role.name}')
        
        # 系统管理员角色
        system_admin_role, created = Role.objects.get_or_create(
            name='系统管理员',
            defaults={'description': '负责系统配置和用户管理的管理员角色'}
        )
        roles['system_admin'] = system_admin_role
        if created:
            self.stdout.write(f'创建角色: {system_admin_role.name}')
        
        # 生产管理员角色
        production_admin_role, created = Role.objects.get_or_create(
            name='生产管理员',
            defaults={'description': '负责生产数据录入和管理的角色'}
        )
        roles['production_admin'] = production_admin_role
        if created:
            self.stdout.write(f'创建角色: {production_admin_role.name}')
        
        # 普通用户角色
        user_role, created = Role.objects.get_or_create(
            name='普通用户',
            defaults={'description': '只能查看基本信息的普通用户角色'}
        )
        roles['user'] = user_role
        if created:
            self.stdout.write(f'创建角色: {user_role.name}')
        
        return roles

    def create_default_permissions(self):
        """创建默认权限"""
        permissions = {}
        
        # 系统设置权限
        system_permissions = [
            ('system_settings_view', '系统设置查看', 'module', '系统设置'),
            ('system_settings_edit', '系统设置编辑', 'operation', '系统设置'),
            ('user_management_view', '用户管理查看', 'module', '用户管理'),
            ('user_management_edit', '用户管理编辑', 'operation', '用户管理'),
            ('rbac_management_view', 'RBAC权限管理查看', 'module', 'RBAC权限管理'),
            ('rbac_management_edit', 'RBAC权限管理编辑', 'operation', 'RBAC权限管理'),
        ]
        
        for code, name, perm_type, module in system_permissions:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'permission_type': perm_type,
                    'module': module,
                    'description': f'{name}权限'
                }
            )
            permissions[code] = permission
            if created:
                self.stdout.write(f'创建权限: {permission.name}')
        
        # 生产管理权限
        production_permissions = [
            ('raw_soil_storage_view', '原土入库查看', 'module', '原土入库'),
            ('raw_soil_storage_edit', '原土入库编辑', 'operation', '原土入库'),
            ('raw_soil_storage_delete', '原土入库删除', 'operation', '原土入库'),
            ('raw_soil_storage_view_own', '原土入库查看自己的', 'data', '原土入库'),
            ('raw_soil_storage_view_all', '原土入库查看全部', 'data', '原土入库'),
            ('production_history_view', '生产历史查看', 'module', '生产历史'),
            ('production_history_view_own', '生产历史查看自己的', 'data', '生产历史'),
            ('production_history_view_all', '生产历史查看全部', 'data', '生产历史'),
            ('qc_report_view', 'QC报表查看', 'module', 'QC报表'),
            ('qc_report_edit', 'QC报表编辑', 'operation', 'QC报表'),
            ('qc_report_export', 'QC报表导出', 'operation', 'QC报表'),
            ('qc_report_view_own', 'QC报表查看自己的', 'data', 'QC报表'),
            ('qc_report_view_all', 'QC报表查看全部', 'data', 'QC报表'),
        ]
        
        for code, name, perm_type, module in production_permissions:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'permission_type': perm_type,
                    'module': module,
                    'description': f'{name}权限'
                }
            )
            permissions[code] = permission
            if created:
                self.stdout.write(f'创建权限: {permission.name}')
        
        # 参数配置权限
        parameter_permissions = [
            ('parameter_config_view', '参数配置查看', 'module', '参数配置'),
            ('parameter_config_edit', '参数配置编辑', 'operation', '参数配置'),
            ('material_mapping_view', '物料映射查看', 'module', '物料映射'),
            ('material_mapping_edit', '物料映射编辑', 'operation', '物料映射'),
            ('warehouse_mapping_view', '仓库映射查看', 'module', '仓库映射'),
            ('warehouse_mapping_edit', '仓库映射编辑', 'operation', '仓库映射'),
        ]
        
        for code, name, perm_type, module in parameter_permissions:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'permission_type': perm_type,
                    'module': module,
                    'description': f'{name}权限'
                }
            )
            permissions[code] = permission
            if created:
                self.stdout.write(f'创建权限: {permission.name}')
        
        return permissions

    def assign_permissions_to_roles(self, roles, permissions):
        """为角色分配权限"""
        
        # 超级管理员拥有所有权限
        admin_role = roles['admin']
        for permission in permissions.values():
            RolePermission.objects.get_or_create(role=admin_role, permission=permission)
        
        # 系统管理员拥有系统管理相关权限
        system_admin_role = roles['system_admin']
        system_permissions = [
            'system_settings_view', 'system_settings_edit',
            'user_management_view', 'user_management_edit',
            'rbac_management_view', 'rbac_management_edit',
            'parameter_config_view', 'parameter_config_edit',
            'material_mapping_view', 'material_mapping_edit',
            'warehouse_mapping_view', 'warehouse_mapping_edit',
        ]
        for perm_code in system_permissions:
            if perm_code in permissions:
                RolePermission.objects.get_or_create(
                    role=system_admin_role, 
                    permission=permissions[perm_code]
                )
        
        # 生产管理员拥有生产相关权限（包括查看全部数据）
        production_admin_role = roles['production_admin']
        production_permissions = [
            'raw_soil_storage_view', 'raw_soil_storage_edit', 'raw_soil_storage_delete',
            'raw_soil_storage_view_all',
            'production_history_view', 'production_history_view_all',
            'qc_report_view', 'qc_report_edit', 'qc_report_export', 'qc_report_view_all',
        ]
        for perm_code in production_permissions:
            if perm_code in permissions:
                RolePermission.objects.get_or_create(
                    role=production_admin_role, 
                    permission=permissions[perm_code]
                )
        
        # 普通用户只有查看自己数据的权限
        user_role = roles['user']
        user_view_permissions = [
            'raw_soil_storage_view_own', 'production_history_view_own', 'qc_report_view_own',
        ]
        for perm_code in user_view_permissions:
            if perm_code in permissions:
                RolePermission.objects.get_or_create(
                    role=user_role, 
                    permission=permissions[perm_code]
                )
        
        self.stdout.write('角色权限分配完成')

    def assign_default_roles_to_users(self):
        """为现有用户分配默认角色"""
        # 为超级用户分配超级管理员角色
        superusers = User.objects.filter(is_superuser=True)
        admin_role = Role.objects.get(name='超级管理员')
        
        for user in superusers:
            UserRole.objects.get_or_create(user=user, role=admin_role)
            self.stdout.write(f'为用户 {user.username} 分配超级管理员角色')
        
        # 为其他用户分配普通用户角色
        normal_users = User.objects.filter(is_superuser=False)
        user_role = Role.objects.get(name='普通用户')
        
        for user in normal_users:
            # 如果用户还没有角色，则分配普通用户角色
            if not UserRole.objects.filter(user=user).exists():
                UserRole.objects.create(user=user, role=user_role)
                self.stdout.write(f'为用户 {user.username} 分配普通用户角色')
        
        self.stdout.write('用户角色分配完成') 