from django.contrib import admin
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta
from .models import TaskLog, QCReportSchedule


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'status', 'created_at', 'execution_time']
    list_filter = ['status', 'task_name', 'created_at']
    search_fields = ['task_name', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')


@admin.register(QCReportSchedule)
class QCReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'recipient_name', 'send_hour', 'send_minute', 'is_enabled', 'is_active']
    list_filter = ['is_enabled', 'report_type', 'created_at']
    search_fields = ['recipient_name', 'recipient_userid']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('report_type', 'is_enabled', 'recipient_userid', 'recipient_name')
        }),
        ('发送时间', {
            'fields': ('send_hour', 'send_minute')
        }),
        ('发送内容', {
            'fields': ('send_excel', 'send_text', 'text_template')
        }),
        ('系统信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # 新建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # 注意：同步到Celery Beat会自动通过信号处理器完成（tasks/signals.py）
        # 信号处理器会在保存后自动触发，后台执行同步
        self.message_user(
            request, 
            f'配置已保存，系统已自动同步到定时任务（后台执行）', 
            level='success'
        )

    def delete_model(self, request, obj):
        # 删除配置（同步到Celery Beat会自动通过信号处理器完成）
        super().delete_model(request, obj)
        self.message_user(
            request, 
            f'配置已删除，系统已自动更新定时任务（后台执行）', 
            level='success'
        )

