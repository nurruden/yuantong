from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from tasks.models import QCReportSchedule
import json


class Command(BaseCommand):
    help = '同步QC报表定时发送配置到Celery Beat'

    def handle(self, *args, **options):
        self.stdout.write('开始同步QC报表定时发送配置...')
        
        # 获取所有启用的配置
        schedules = QCReportSchedule.objects.filter(is_enabled=True)
        
        synced_count = 0
        for schedule in schedules:
            try:
                # 创建或更新crontab调度
                crontab, created = CrontabSchedule.objects.get_or_create(
                    hour=schedule.send_hour,
                    minute=schedule.send_minute,
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )
                
                # 创建或更新定时任务
                task_name = f'qc-report-{schedule.report_type}'
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
                self.stdout.write(
                    self.style.SUCCESS(f'{status}任务: {task_name} - {schedule.get_report_type_display()} - {schedule.send_hour:02d}:{schedule.send_minute:02d}')
                )
                synced_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'同步配置失败: {schedule.get_report_type_display()} - {str(e)}')
                )
        
        # 清理已删除的配置对应的任务
        all_qc_tasks = PeriodicTask.objects.filter(name__startswith='qc-report-')
        for task in all_qc_tasks:
            report_type = task.name.replace('qc-report-', '')
            if not QCReportSchedule.objects.filter(report_type=report_type, is_enabled=True).exists():
                task.delete()
                self.stdout.write(
                    self.style.WARNING(f'删除过期任务: {task.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'同步完成！共处理 {synced_count} 个配置')
        )
