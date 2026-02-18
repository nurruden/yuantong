from django.core.management.base import BaseCommand
from home.models import Parameter
import json

class Command(BaseCommand):
    help = '设置跨用户编辑权限'

    def add_arguments(self, parser):
        parser.add_argument(
            '--enable',
            action='store_true',
            help='启用跨用户编辑功能',
        )
        parser.add_argument(
            '--disable',
            action='store_true',
            help='禁用跨用户编辑功能',
        )
        parser.add_argument(
            '--edit-limit',
            type=int,
            default=7,
            help='设置编辑期限（天数）',
        )
        parser.add_argument(
            '--module',
            type=str,
            help='指定模块（如：dongtai_qc_report）',
        )
        parser.add_argument(
            '--grant-edit-others',
            action='store_true',
            help='为指定模块授予跨用户编辑权限',
        )

    def handle(self, *args, **options):
        if options['enable']:
            # 启用跨用户编辑功能
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': 'true'}
            )
            self.stdout.write(
                self.style.SUCCESS('✅ 已启用跨用户编辑功能')
            )

        if options['disable']:
            # 禁用跨用户编辑功能
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': 'false'}
            )
            self.stdout.write(
                self.style.SUCCESS('✅ 已禁用跨用户编辑功能')
            )

        # 设置编辑期限
        edit_limit = options['edit_limit']
        Parameter.objects.update_or_create(
            id='report_edit_limit',
            defaults={'value': str(edit_limit)}
        )
        self.stdout.write(
            self.style.SUCCESS(f'✅ 已设置编辑期限为 {edit_limit} 天')
        )

        # 为指定模块设置跨用户编辑权限
        if options['module'] and options['grant_edit_others']:
            module = options['module']
            permissions = {
                'view': True,
                'edit': True,
                'edit_others': True,
                'delete': True,
                'manage': True
            }
            
            Parameter.objects.update_or_create(
                id=f'{module}_permissions',
                defaults={'value': json.dumps(permissions)}
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ 已为 {module} 模块授予跨用户编辑权限')
            )

        # 显示当前设置
        self.show_current_settings()

    def show_current_settings(self):
        """显示当前权限设置"""
        self.stdout.write('\n📋 当前权限设置：')
        
        # 跨用户编辑状态
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        cross_edit_status = '启用' if cross_edit_param and cross_edit_param.value == 'true' else '禁用'
        self.stdout.write(f'   跨用户编辑功能: {cross_edit_status}')
        
        # 编辑期限
        edit_limit_param = Parameter.objects.filter(id='report_edit_limit').first()
        edit_limit = edit_limit_param.value if edit_limit_param else '7'
        self.stdout.write(f'   编辑期限: {edit_limit} 天')
        
        # 模块权限
        modules = [
            'yuantong_qc_report', 'dayuan_qc_report', 'dongtai_qc_report',
            'xinghui_qc_report', 'changfu_qc_report', 'yuantong2_qc_report',
            'xinghui2_qc_report'
        ]
        
        module_names = {
            'yuantong_qc_report': '远通QC报表',
            'dayuan_qc_report': '大塬QC报表',
            'dongtai_qc_report': '东泰QC报表',
            'xinghui_qc_report': '兴辉QC报表',
            'changfu_qc_report': '长富QC报表',
            'yuantong2_qc_report': '远通二线QC报表',
            'xinghui2_qc_report': '兴辉二线QC报表'
        }
        
        self.stdout.write('\n📊 模块权限状态：')
        for module in modules:
            param = Parameter.objects.filter(id=f'{module}_permissions').first()
            if param and param.value:
                try:
                    permissions = json.loads(param.value)
                    edit_others = '✅' if permissions.get('edit_others', False) else '❌'
                    self.stdout.write(f'   {module_names.get(module, module)}: {edit_others}')
                except:
                    self.stdout.write(f'   {module_names.get(module, module)}: ❌ (配置错误)')
            else:
                self.stdout.write(f'   {module_names.get(module, module)}: ❌ (未配置)')

