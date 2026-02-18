"""
检查 Celery Beat 和 Worker 状态
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask
from tasks.models import TaskLog
from datetime import datetime, timedelta
import subprocess
import os


class Command(BaseCommand):
    help = '检查 Celery Beat 和 Worker 状态'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('Celery 状态检查'))
        self.stdout.write('='*60 + '\n')
        
        # 1. 检查 Celery Beat 进程
        self.stdout.write('\n[1] 检查 Celery Beat 进程...')
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            beat_processes = [line for line in result.stdout.split('\n') if 'celery' in line.lower() and 'beat' in line.lower() and 'python' in line.lower()]
            if beat_processes:
                self.stdout.write(self.style.SUCCESS(f'  ✅ 找到 {len(beat_processes)} 个 Celery Beat 进程:'))
                for proc in beat_processes:
                    self.stdout.write(f'    {proc}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ Celery Beat 进程未运行！'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 检查进程失败: {str(e)}'))
        
        # 2. 检查 Celery Worker 进程
        self.stdout.write('\n[2] 检查 Celery Worker 进程...')
        try:
            worker_processes = [line for line in result.stdout.split('\n') if 'celery' in line.lower() and 'worker' in line.lower() and 'beat' not in line.lower() and 'python' in line.lower()]
            if worker_processes:
                self.stdout.write(self.style.SUCCESS(f'  ✅ 找到 {len(worker_processes)} 个 Celery Worker 进程:'))
                for proc in worker_processes[:3]:  # 只显示前3个
                    self.stdout.write(f'    {proc}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ Celery Worker 进程未运行！'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 检查进程失败: {str(e)}'))
        
        # 3. 检查定时任务状态
        self.stdout.write('\n[3] 检查定时任务状态...')
        tasks = PeriodicTask.objects.filter(enabled=True)
        if tasks.count() > 0:
            self.stdout.write(f'  找到 {tasks.count()} 个启用的定时任务:')
            for task in tasks[:10]:  # 只显示前10个
                status = self.style.SUCCESS('✅ 启用') if task.enabled else self.style.ERROR('❌ 禁用')
                if task.crontab:
                    time_str = f'{str(task.crontab.hour).zfill(2)}:{str(task.crontab.minute).zfill(2)}'
                    last_run = task.last_run_at.strftime('%Y-%m-%d %H:%M:%S') if task.last_run_at else '从未运行'
                    self.stdout.write(
                        f'    - {task.name}: {time_str}, {status}, 上次运行: {last_run}'
                    )
                else:
                    self.stdout.write(f'    - {task.name}: {status} (无时间配置)')
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  没有找到启用的定时任务'))
        
        # 4. 检查最近的任务执行日志
        self.stdout.write('\n[4] 检查最近的任务执行日志...')
        recent_logs = TaskLog.objects.all().order_by('-created_at')[:10]
        
        if recent_logs.count() > 0:
            self.stdout.write(f'  最近 {recent_logs.count()} 条日志:')
            for log in recent_logs:
                status_color = self.style.SUCCESS if log.status == 'success' else (
                    self.style.ERROR if log.status == 'failed' else self.style.WARNING
                )
                status_text = {'success': '✅ 成功', 'failed': '❌ 失败', 'running': '⏳ 运行中'}.get(log.status, log.status)
                self.stdout.write(
                    f'    [{log.created_at.strftime("%Y-%m-%d %H:%M:%S")}] '
                    f'{status_color(status_text)} - {log.message[:80]}'
                )
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  没有找到任务执行日志'))
        
        # 5. 检查日志文件
        self.stdout.write('\n[5] 检查日志文件...')
        log_files = {
            'Celery Beat': ['logs/celery_beat.log', '/var/www/yuantong/logs/celery_beat.log'],
            'Celery Worker': ['logs/celery_worker.log', '/var/www/yuantong/logs/celery_worker.log'],
            'Django': ['logs/django.log', '/var/www/yuantong/logs/django.log'],
        }
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        for log_name, log_paths in log_files.items():
            found = False
            for log_path in log_paths:
                if not os.path.isabs(log_path):
                    full_path = os.path.join(base_dir, log_path)
                else:
                    full_path = log_path
                
                if os.path.exists(full_path):
                    found = True
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            if lines:
                                self.stdout.write(f'  {log_name} ({full_path}):')
                                self.stdout.write(f'    最后3行:')
                                for line in lines[-3:]:
                                    if line.strip():
                                        self.stdout.write(f'      {line.strip()[:150]}')
                            else:
                                self.stdout.write(f'  {log_name}: 文件为空')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  {log_name}: 读取失败 - {str(e)}'))
                    break
            
            if not found:
                self.stdout.write(self.style.WARNING(f'  {log_name}: 日志文件不存在'))
        
        # 6. 建议
        self.stdout.write('\n[6] 建议...')
        if not beat_processes:
            self.stdout.write('  ❌ Celery Beat 未运行，需要启动:')
            self.stdout.write('     python manage.py restart_celery_beat')
        
        if not worker_processes:
            self.stdout.write('  ❌ Celery Worker 未运行，需要启动:')
            self.stdout.write('     celery -A yuantong worker -l info')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('检查完成')
        self.stdout.write('='*60 + '\n')
