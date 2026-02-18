from django.core.management.base import BaseCommand
from home.models import MenuPermission


class Command(BaseCommand):
    help = '初始化系统权限配置'

    def handle(self, *args, **options):
        """初始化权限配置"""
        self.stdout.write(self.style.SUCCESS('开始初始化权限配置...'))
        
        # 创建系统设置权限配置
        permission, created = MenuPermission.objects.update_or_create(
            menu_name='系统设置',
            is_active=True,
            defaults={
                'allowed_users': 'GaoBieKeLe,yanyanzhao',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'已创建系统设置权限配置: {permission}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'系统设置权限配置已存在: {permission}')
            )
        
        self.stdout.write(self.style.SUCCESS('权限配置初始化完成！'))
        self.stdout.write(
            self.style.SUCCESS('当前有权限访问系统设置的用户: GaoBieKeLe, yanyanzhao')
        )
        self.stdout.write(
            self.style.SUCCESS('您可以通过权限配置页面修改用户权限设置')
        ) 