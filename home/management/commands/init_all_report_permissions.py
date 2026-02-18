from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from system.models import (
    Company, Department, Position, UserProfile, 
    Role, Permission, UserRole, RolePermission,
    CompanyPermission, DepartmentPermission, PositionPermission
)

class Command(BaseCommand):
    help = '为所有QC报表初始化基于公司、部门的权限系统'

    def handle(self, *args, **options):
        self.stdout.write('开始为所有QC报表初始化权限系统...')
        
        # 创建公司
        companies = self.create_companies()
        
        # 创建部门和职位
        departments, positions = self.create_departments_and_positions(companies)
        
        # 创建权限
        permissions = self.create_permissions()
        
        # 为角色分配权限
        self.assign_permissions_to_roles(permissions)
        
        # 为公司、部门、职位分配权限
        self.assign_permissions_to_organizations(companies, departments, positions, permissions)
        
        # 为现有用户分配公司、部门、职位信息
        self.assign_organization_to_users(companies, departments, positions)
        
        self.stdout.write(self.style.SUCCESS('所有QC报表权限系统初始化完成！'))

    def create_companies(self):
        """创建公司"""
        companies = {}
        
        # 大塬公司
        dayuan_company, created = Company.objects.get_or_create(
            code='DAYUAN',
            defaults={
                'name': '大塬公司',
                'description': '大塬公司及其下属部门'
            }
        )
        companies['dayuan'] = dayuan_company
        if created:
            self.stdout.write(f'创建公司: {dayuan_company.name}')
        
        # 远通公司
        yuantong_company, created = Company.objects.get_or_create(
            code='YUANTONG',
            defaults={
                'name': '远通公司',
                'description': '远通公司及其下属部门'
            }
        )
        companies['yuantong'] = yuantong_company
        if created:
            self.stdout.write(f'创建公司: {yuantong_company.name}')
        
        # 东泰公司
        dongtai_company, created = Company.objects.get_or_create(
            code='DONGTAI',
            defaults={
                'name': '东泰公司',
                'description': '东泰公司及其下属部门'
            }
        )
        companies['dongtai'] = dongtai_company
        if created:
            self.stdout.write(f'创建公司: {dongtai_company.name}')
        
        # 兴辉公司
        xinghui_company, created = Company.objects.get_or_create(
            code='XINGHUI',
            defaults={
                'name': '兴辉公司',
                'description': '兴辉公司及其下属部门'
            }
        )
        companies['xinghui'] = xinghui_company
        if created:
            self.stdout.write(f'创建公司: {xinghui_company.name}')
        
        # 长富公司
        changfu_company, created = Company.objects.get_or_create(
            code='CHANGFU',
            defaults={
                'name': '长富公司',
                'description': '长富公司及其下属部门'
            }
        )
        companies['changfu'] = changfu_company
        if created:
            self.stdout.write(f'创建公司: {changfu_company.name}')
        
        return companies

    def create_departments_and_positions(self, companies):
        """创建部门和职位"""
        departments = {}
        positions = {}
        
        # 为每个公司创建QC部门和管理部门
        for company_name, company in companies.items():
            # QC部门
            qc_dept, created = Department.objects.get_or_create(
                company=company,
                code='QC',
                defaults={
                    'name': f'{company.name}QC部门',
                    'description': f'{company.name}QC部门，负责质量检测',
                    'level': 1
                }
            )
            departments[f'{company_name}_qc'] = qc_dept
            if created:
                self.stdout.write(f'创建部门: {qc_dept.name}')
            
            # 管理部
            manage_dept, created = Department.objects.get_or_create(
                company=company,
                code='MANAGE',
                defaults={
                    'name': f'{company.name}管理部',
                    'description': f'{company.name}管理部，负责公司管理',
                    'level': 1
                }
            )
            departments[f'{company_name}_manage'] = manage_dept
            if created:
                self.stdout.write(f'创建部门: {manage_dept.name}')
            
            # QC记录员职位
            qc_recorder, created = Position.objects.get_or_create(
                company=company,
                department=qc_dept,
                code='QC_RECORDER',
                defaults={
                    'name': f'{company.name}QC记录员',
                    'description': f'负责{company.name}QC报表的记录工作',
                    'level': 1
                }
            )
            positions[f'{company_name}_qc_recorder'] = qc_recorder
            if created:
                self.stdout.write(f'创建职位: {qc_recorder.name}')
            
            # 经理职位
            manager, created = Position.objects.get_or_create(
                company=company,
                department=manage_dept,
                code='MANAGER',
                defaults={
                    'name': f'{company.name}经理',
                    'description': f'{company.name}经理，负责公司管理',
                    'level': 2
                }
            )
            positions[f'{company_name}_manager'] = manager
            if created:
                self.stdout.write(f'创建职位: {manager.name}')
        
        return departments, positions

    def create_permissions(self):
        """创建权限"""
        permissions = {}
        
        # 定义所有报表的权限
        report_permissions = {
            'dayuan_qc_report': '大塬QC报表',
            'dongtai_qc_report': '东泰QC报表',
            'yuantong_qc_report': '远通QC报表',
            'yuantong2_qc_report': '远通二线QC报表',
            'xinghui_qc_report': '兴辉QC报表',
            'xinghui2_qc_report': '兴辉二线QC报表',
            'changfu_qc_report': '长富QC报表',
        }
        
        # 为每个报表创建权限
        for report_code, report_name in report_permissions.items():
            report_permissions_list = [
                (f'{report_code}_view', f'{report_name}查看', 'module', report_name),
                (f'{report_code}_edit', f'{report_name}编辑', 'operation', report_name),
                (f'{report_code}_delete', f'{report_name}删除', 'operation', report_name),
                (f'{report_code}_export', f'{report_name}导出', 'operation', report_name),
                (f'{report_code}_view_own', f'{report_name}查看自己的', 'data', report_name),
                (f'{report_code}_view_department', f'{report_name}查看部门', 'data', report_name),
                (f'{report_code}_view_company', f'{report_name}查看公司', 'data', report_name),
                (f'{report_code}_view_all', f'{report_name}查看全部', 'data', report_name),
            ]
            
            for code, name, perm_type, module in report_permissions_list:
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

    def assign_permissions_to_roles(self, permissions):
        """为角色分配权限"""
        # 获取或创建角色
        admin_role, _ = Role.objects.get_or_create(name='超级管理员')
        system_admin_role, _ = Role.objects.get_or_create(name='系统管理员')
        
        # 超级管理员拥有所有权限
        for permission in permissions.values():
            RolePermission.objects.get_or_create(role=admin_role, permission=permission)
        
        # 系统管理员拥有查看权限
        system_permissions = []
        for perm_code in permissions.keys():
            if perm_code.endswith('_view') or perm_code.endswith('_view_all') or perm_code.endswith('_export'):
                system_permissions.append(perm_code)
        
        for perm_code in system_permissions:
            if perm_code in permissions:
                RolePermission.objects.get_or_create(
                    role=system_admin_role, 
                    permission=permissions[perm_code]
                )
        
        self.stdout.write('角色权限分配完成')

    def assign_permissions_to_organizations(self, companies, departments, positions, permissions):
        """为公司、部门、职位分配权限"""
        
        # 为每个公司的QC记录员分配权限
        for company_name in companies.keys():
            qc_recorder = positions.get(f'{company_name}_qc_recorder')
            if qc_recorder:
                qc_recorder_permissions = [
                    f'{company_name}_qc_report_view', f'{company_name}_qc_report_edit', 
                    f'{company_name}_qc_report_delete', f'{company_name}_qc_report_view_own'
                ]
                for perm_code in qc_recorder_permissions:
                    if perm_code in permissions:
                        PositionPermission.objects.get_or_create(
                            position=qc_recorder,
                            permission=permissions[perm_code]
                        )
        
        # 为每个公司的经理分配权限
        for company_name in companies.keys():
            manager = positions.get(f'{company_name}_manager')
            if manager:
                manager_permissions = [
                    f'{company_name}_qc_report_view', f'{company_name}_qc_report_view_company'
                ]
                for perm_code in manager_permissions:
                    if perm_code in permissions:
                        PositionPermission.objects.get_or_create(
                            position=manager,
                            permission=permissions[perm_code]
                        )
        
        # 为每个公司的QC部门分配权限
        for company_name in companies.keys():
            qc_dept = departments.get(f'{company_name}_qc')
            if qc_dept:
                dept_permissions = [
                    f'{company_name}_qc_report_view', f'{company_name}_qc_report_view_department'
                ]
                for perm_code in dept_permissions:
                    if perm_code in permissions:
                        DepartmentPermission.objects.get_or_create(
                            department=qc_dept,
                            permission=permissions[perm_code]
                        )
        
        # 为每个公司分配权限
        for company_name, company in companies.items():
            company_permissions = [
                f'{company_name}_qc_report_view', f'{company_name}_qc_report_view_company'
            ]
            for perm_code in company_permissions:
                if perm_code in permissions:
                    CompanyPermission.objects.get_or_create(
                        company=company,
                        permission=permissions[perm_code]
                    )
        
        self.stdout.write('组织权限分配完成')

    def assign_organization_to_users(self, companies, departments, positions):
        """为现有用户分配公司、部门、职位信息"""
        
        # 为现有用户分配默认的组织信息
        users = User.objects.all()
        
        # 默认分配到第一个公司
        default_company = list(companies.values())[0]
        default_dept = list(departments.values())[0]
        default_position = list(positions.values())[0]
        
        for user in users:
            # 如果用户还没有档案信息，创建默认档案
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company': default_company,
                    'department': default_dept,
                    'position': default_position,
                    'employee_id': f'EMP{user.id:04d}',
                    'is_active': True
                }
            )
            
            # 如果用户已有档案但公司信息为空，则更新
            if not created and not profile.company:
                profile.company = default_company
                profile.department = default_dept
                profile.position = default_position
                profile.save()
                self.stdout.write(f'更新用户 {user.username} 的组织信息')
            elif created:
                self.stdout.write(f'为用户 {user.username} 创建档案信息')
        
        self.stdout.write('用户组织信息分配完成') 