"""
测试大塬QC报表发送功能的管理命令
使用方法: python manage.py test_dayuan_report
"""
from django.core.management.base import BaseCommand
from tasks.tasks import send_daily_dayuan_report


class Command(BaseCommand):
    help = '测试大塬QC报表发送功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='异步执行任务',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('开始测试大塬QC报表发送功能...')
        )
        
        try:
            if options['async']:
                # 异步执行
                task = send_daily_dayuan_report.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'任务已提交，任务ID: {task.id}')
                )
            else:
                # 同步执行
                result = send_daily_dayuan_report()
                self.stdout.write(
                    self.style.SUCCESS(f'任务执行完成: {result}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'任务执行失败: {str(e)}')
            )
