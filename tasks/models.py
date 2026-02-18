from django.db import models
from django.contrib.auth.models import User


class TaskLog(models.Model):
    """定时任务执行日志"""
    task_name = models.CharField('任务名称', max_length=100)
    status = models.CharField('执行状态', max_length=20, choices=[
        ('success', '成功'),
        ('failed', '失败'),
        ('running', '执行中'),
    ])
    message = models.TextField('执行消息', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    execution_time = models.FloatField('执行时间(秒)', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '任务日志'
        verbose_name_plural = '任务日志'
    
    def __str__(self):
        return f"{self.task_name} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class QCReportSchedule(models.Model):
    """QC报表定时发送配置"""

    REPORT_TYPES = [
        ('dayuan', '大塬QC报表'),
        ('dongtai', '东泰QC报表'),
        ('changfu', '长富QC报表'),
        ('xinghui', '兴辉QC报表'),
        ('xinghui2', '兴辉二线QC报表'),
        ('yuantong', '远通QC报表'),
        ('yuantong2', '远通二线QC报表'),
    ]

    report_type = models.CharField('报表类型', max_length=20, choices=REPORT_TYPES)
    is_enabled = models.BooleanField('是否启用', default=True)
    send_hour = models.IntegerField('发送小时', default=8, help_text='24小时制，0-23')
    send_minute = models.IntegerField('发送分钟', default=0, help_text='0-59')
    recipient_userid = models.CharField('接收人UserID', max_length=100, help_text='企业微信用户ID')
    recipient_name = models.CharField('接收人姓名', max_length=100, help_text='接收人显示名称')
    send_excel = models.BooleanField('发送Excel文件', default=True)
    send_text = models.BooleanField('发送文本消息', default=True)
    text_template = models.TextField('文本消息模板', blank=True, help_text='留空使用默认模板')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')

    class Meta:
        ordering = ['report_type', 'recipient_name']
        verbose_name = 'QC报表定时发送配置'
        verbose_name_plural = 'QC报表定时发送配置'
        unique_together = [['report_type', 'recipient_userid']]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.recipient_name} - {self.send_hour:02d}:{self.send_minute:02d}"

    @property
    def cron_expression(self):
        """获取cron表达式"""
        return f"{self.send_minute} {self.send_hour} * * *"

    @property
    def is_active(self):
        """检查是否激活"""
        return self.is_enabled and self.recipient_userid
