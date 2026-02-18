#!/usr/bin/env python
"""
同步QC报表配置到Celery Beat定时任务
使用方法：python sync_qc_schedules.py
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, CrontabSchedule
from tasks.models import QCReportSchedule
import json

def sync_all_schedules():
    """同步所有配置到定时任务"""
    print("=== 开始同步所有QC报表配置 ===")
    
    # 获取所有启用的配置
    schedules = QCReportSchedule.objects.filter(is_enabled=True)
    
    synced_count = 0
    for schedule in schedules:
        try:
            # 创建crontab调度
            crontab, created = CrontabSchedule.objects.get_or_create(
                hour=schedule.send_hour,
                minute=schedule.send_minute,
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
                timezone='Asia/Shanghai'
            )
            
            # 创建任务名称
            if schedule.send_hour == 8 and schedule.send_minute == 0:
                task_name = f'qc-report-{schedule.report_type}'
            else:
                task_name = f'qc-report-{schedule.report_type}-{schedule.send_hour:02d}{schedule.send_minute:02d}'
            
            # 创建或更新定时任务
            task, created = PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    'task': 'tasks.tasks.send_qc_report_by_schedule',
                    'crontab': crontab,
                    'args': json.dumps([schedule.report_type]),
                    'enabled': schedule.is_enabled,
                    'queue': 'default',
                    'routing_key': 'default',
                }
            )
            
            status = '创建' if created else '更新'
            print(f"✅ {status}任务: {task_name} - {schedule.get_report_type_display()} - {schedule.send_hour:02d}:{schedule.send_minute:02d}")
            synced_count += 1
            
        except Exception as e:
            print(f"❌ 同步失败 {schedule.report_type}: {e}")
    
    print(f"\n=== 同步完成！共处理 {synced_count} 个配置 ===")
    
    # 显示所有定时任务
    print("\n=== 当前所有定时任务 ===")
    tasks = PeriodicTask.objects.filter(name__contains='qc-report').order_by('name')
    for task in tasks:
        print(f"{task.name}: {task.enabled} - {task.crontab}")

def restart_celery_beat():
    """重启Celery Beat服务"""
    import subprocess
    print("\n=== 重启Celery Beat服务 ===")
    try:
        # 停止现有服务
        subprocess.run(['pkill', '-f', 'celery.*beat'], check=False)
        print("✅ 已停止现有Celery Beat服务")
        
        # 启动新服务
        subprocess.run([
            'nohup', 'celery', '-A', 'yuantong', 'beat',
            '--loglevel=info',
            '--logfile=/var/www/yuantong/logs/celery_beat.log',
            '--pidfile=/var/www/yuantong/celery_beat.pid',
            '--detach',
            '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler'
        ], cwd='/var/www/yuantong', check=True)
        print("✅ 已启动新的Celery Beat服务")
        
    except Exception as e:
        print(f"❌ 重启服务失败: {e}")

if __name__ == '__main__':
    sync_all_schedules()
    restart_celery_beat()
    print("\n🎉 同步完成！所有配置已生效。")
