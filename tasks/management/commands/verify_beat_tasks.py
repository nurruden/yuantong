"""
验证 Celery Beat 是否正确加载了任务
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = '验证 Celery Beat 是否正确加载了定时任务'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('验证 Celery Beat 任务加载'))
        self.stdout.write('='*60 + '\n')
        
        now_utc = timezone.now()
        now_local = timezone.localtime(now_utc)
        self.stdout.write(f'\n当前时间 (UTC): {now_utc.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'当前时间 (本地): {now_local.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'时区: {timezone.get_current_timezone()}\n')
        
        # 使用本地时间进行计算
        now = now_local
        
        # 检查所有定时任务
        tasks = PeriodicTask.objects.filter(enabled=True)
        
        if tasks.count() == 0:
            self.stdout.write(self.style.ERROR('\n❌ 没有找到启用的定时任务'))
            return
        
        self.stdout.write(f'\n找到 {tasks.count()} 个启用的定时任务:\n')
        
        enabled_tasks = []
        disabled_tasks = []
        
        for task in tasks:
            if task.crontab:
                hour = int(task.crontab.hour)
                minute = int(task.crontab.minute)
                time_str = f'{str(hour).zfill(2)}:{str(minute).zfill(2)}'
                
                # 计算下次运行时间（使用本地时间）
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    # 如果今天的时间已过，设置为明天
                    next_run += timedelta(days=1)
                
                time_until = next_run - now
                hours_until = time_until.total_seconds() / 3600
                minutes_until = time_until.total_seconds() / 60
                
                info = {
                    'task': task,
                    'time': time_str,
                    'next_run': next_run,
                    'hours_until': hours_until,
                    'minutes_until': minutes_until
                }
                
                if task.enabled:
                    enabled_tasks.append(info)
                else:
                    disabled_tasks.append(info)
        
        # 显示启用的任务
        if enabled_tasks:
            self.stdout.write(self.style.SUCCESS('✅ 启用的任务:'))
            for info in enabled_tasks:
                # 转换上次运行时间为本地时间
                if info['task'].last_run_at:
                    last_run_local = timezone.localtime(info['task'].last_run_at)
                    last_run = last_run_local.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    last_run = '从未运行'
                status_icon = '✅' if info['task'].last_run_at else '⏳'
                
                # 格式化时间差
                if info["hours_until"] < 1:
                    time_until_str = f'约 {info["minutes_until"]:.0f} 分钟后'
                elif info["hours_until"] < 24:
                    time_until_str = f'约 {info["hours_until"]:.1f} 小时后'
                else:
                    days = int(info["hours_until"] // 24)
                    hours = info["hours_until"] % 24
                    time_until_str = f'约 {days} 天 {hours:.1f} 小时后'
                
                self.stdout.write(
                    f'  {status_icon} {info["task"].name}: '
                    f'{info["time"]}, '
                    f'上次运行: {last_run}, '
                    f'下次运行: {info["next_run"].strftime("%Y-%m-%d %H:%M:%S")} '
                    f'({time_until_str})'
                )
        else:
            self.stdout.write(self.style.WARNING('⚠️  没有启用的任务'))
        
        # 显示禁用的任务
        if disabled_tasks:
            self.stdout.write(self.style.ERROR('\n❌ 禁用的任务:'))
            for info in disabled_tasks:
                self.stdout.write(f'  - {info["task"].name}: {info["time"]}')
        
        # 检查是否有任务在最近执行过
        self.stdout.write('\n' + '-'*60)
        recently_run = [info for info in enabled_tasks if info['task'].last_run_at]
        if recently_run:
            self.stdout.write('\n最近执行过的任务:')
            for info in recently_run:
                if info['task'].last_run_at:
                    last_run_local = timezone.localtime(info['task'].last_run_at)
                    last_run = last_run_local.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    last_run = '从未运行'
                self.stdout.write(f'  ✅ {info["task"].name}: {last_run}')
        else:
            self.stdout.write('\n⚠️  没有任务在最近执行过')
            self.stdout.write('   这可能意味着:')
            self.stdout.write('   1. 任务刚刚创建，还没到执行时间')
            self.stdout.write('   2. Celery Beat 需要重新加载任务')
            self.stdout.write('   3. 任务执行时出错（检查日志）')
        
        # 总结
        self.stdout.write('\n' + '='*60)
        self.stdout.write('验证完成')
        self.stdout.write('='*60 + '\n')
        
        if enabled_tasks:
            next_task = min(enabled_tasks, key=lambda x: x['hours_until'])
            
            # 格式化时间差
            if next_task["hours_until"] < 1:
                time_until_str = f'约 {next_task["minutes_until"]:.0f} 分钟后'
            elif next_task["hours_until"] < 24:
                time_until_str = f'约 {next_task["hours_until"]:.1f} 小时后'
            else:
                days = int(next_task["hours_until"] // 24)
                hours = next_task["hours_until"] % 24
                time_until_str = f'约 {days} 天 {hours:.1f} 小时后'
            
            self.stdout.write(f'\n📅 下一个任务: {next_task["task"].name}')
            self.stdout.write(f'⏰ 执行时间: {next_task["next_run"].strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write(f'⏳ 距离现在: {time_until_str}\n')
