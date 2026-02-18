"""
Celery定时任务配置
"""
from celery.schedules import crontab
from celery import Celery
import os

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')

app = Celery('yuantong')

# 从Django设置中加载Celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 定时任务配置
app.conf.beat_schedule = {
    'send-daily-dayuan-report': {
        'task': 'tasks.tasks.send_daily_dayuan_report',
        'schedule': crontab(hour=8, minute=0),  # 每天早晨8点执行
        'options': {
            'queue': 'default',
            'routing_key': 'default',
        }
    },
}

# 时区设置
app.conf.timezone = 'Asia/Shanghai'

# 任务结果过期时间
app.conf.result_expires = 3600

# 任务序列化
app.conf.task_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_serializer = 'json'

# 任务路由
app.conf.task_routes = {
    'tasks.tasks.*': {'queue': 'default'},
}
