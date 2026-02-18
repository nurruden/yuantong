"""
检查和修复时区问题
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = '检查时区配置是否正确'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('时区配置检查'))
        self.stdout.write('='*60 + '\n')
        
        # 1. 检查 Django 设置
        self.stdout.write('\n[1] Django 设置:')
        self.stdout.write(f'  TIME_ZONE: {settings.TIME_ZONE}')
        self.stdout.write(f'  USE_TZ: {settings.USE_TZ}')
        
        # 2. 检查当前时间
        self.stdout.write('\n[2] 时间对比:')
        django_now = timezone.now()
        django_local = timezone.localtime(django_now)
        system_now = datetime.now()
        
        self.stdout.write(f'  Django UTC: {django_now.strftime("%Y-%m-%d %H:%M:%S %Z")}')
        self.stdout.write(f'  Django 本地 ({timezone.get_current_timezone()}): {django_local.strftime("%Y-%m-%d %H:%M:%S %Z")}')
        self.stdout.write(f'  系统时间: {system_now.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # 3. 计算时差
        time_diff = (system_now - django_local.replace(tzinfo=None)).total_seconds() / 3600
        self.stdout.write(f'\n  时差: {time_diff:.1f} 小时')
        
        if abs(time_diff) > 1:
            self.stdout.write(self.style.ERROR(f'\n  ⚠️  警告: Django 时间与系统时间相差 {time_diff:.1f} 小时！'))
            self.stdout.write('\n  可能的原因:')
            self.stdout.write('    1. USE_TZ=True 但系统时间不是 UTC')
            self.stdout.write('    2. TIME_ZONE 设置不正确')
            self.stdout.write('    3. 数据库时区设置不正确')
        else:
            self.stdout.write(self.style.SUCCESS('\n  ✅ 时区配置正确'))
        
        # 4. 建议
        self.stdout.write('\n[3] 建议:')
        if settings.USE_TZ:
            self.stdout.write('  ✅ USE_TZ=True (推荐设置)')
            self.stdout.write('  📝 确保 TIME_ZONE 设置为正确的时区')
            if settings.TIME_ZONE != 'Asia/Shanghai':
                self.stdout.write(self.style.WARNING(f'    当前 TIME_ZONE={settings.TIME_ZONE}，建议设置为 Asia/Shanghai'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  USE_TZ=False (不推荐)'))
            self.stdout.write('  📝 建议设置 USE_TZ=True 并设置正确的 TIME_ZONE')
        
        self.stdout.write('\n  检查 settings.py 中的设置:')
        self.stdout.write('    TIME_ZONE = "Asia/Shanghai"')
        self.stdout.write('    USE_TZ = True')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('检查完成')
        self.stdout.write('='*60 + '\n')


