#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为指定用户授予 QC 报表查看与编辑权限（用于模板导出、历史导入、新数据录入等）。
依赖 system 应用的 Role / Permission / UserRole / RolePermission。
用法:
  python manage.py grant_qc_report_permission GaoBieKeLe
  python manage.py grant_qc_report_permission --username GaoBieKeLe
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from system.models import Permission, Role, RolePermission, UserRole


# QC 报表相关权限代码（与 home.utils.permissions / qc_reports 中一致）
QC_PERMISSION_CODES = [
    'qc_report_view',   # 查看、导出、下载模板等
    'qc_report_edit',    # 编辑、导入、创建、删除等
]


class Command(BaseCommand):
    help = '为指定用户授予 QC 报表查看与编辑权限'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', help='用户名')
        parser.add_argument('--username', dest='username_opt', help='用户名')

    def handle(self, *args, **options):
        username = options.get('username_opt') or options.get('username') or (args[0] if args else None)
        if not username:
            self.stderr.write('请提供用户名。示例: python manage.py grant_qc_report_permission GaoBieKeLe')
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'用户不存在: {username}'))
            return

        # 1. 确保权限存在
        perms = []
        for code in QC_PERMISSION_CODES:
            perm, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'name': 'QC报表查看' if code == 'qc_report_view' else 'QC报表编辑',
                    'permission_type': 'module' if code == 'qc_report_view' else 'operation',
                    'module': 'QC报表',
                    'description': f'{code} 权限',
                },
            )
            perms.append(perm)
            if created:
                self.stdout.write(f'  创建权限: {perm.name} ({perm.code})')

        # 2. 确保角色存在并拥有上述权限
        role, role_created = Role.objects.get_or_create(
            name='QC报表操作员',
            defaults={'description': '可查看与编辑 QC 报表（模板导出、导入、新数据录入）'},
        )
        if role_created:
            self.stdout.write(f'  创建角色: {role.name}')
        for perm in perms:
            RolePermission.objects.get_or_create(role=role, permission=perm)

        # 3. 为用户分配该角色
        ur, ur_created = UserRole.objects.get_or_create(user=user, role=role)
        if ur_created:
            self.stdout.write(self.style.SUCCESS(f'已为用户 {username} 分配角色「{role.name}」，现具备 QC 报表查看与编辑权限。'))
        else:
            self.stdout.write(self.style.SUCCESS(f'用户 {username} 已拥有角色「{role.name}」，权限无需变更。'))
