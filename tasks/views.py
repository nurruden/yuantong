"""
任务管理视图
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import TaskLog, QCReportSchedule
from .tasks import send_daily_dayuan_report
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
import logging


def sync_schedule_to_celery_beat(schedule):
    """同步单个配置到Celery Beat定时任务"""
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
        
        return True, f"同步成功: {task_name}"
        
    except Exception as e:
        return False, f"同步失败: {str(e)}"


@login_required
def task_management(request):
    """任务管理页面"""
    from home.utils.permissions import filter_menu_by_permission
    from home.config import MENU_ITEMS
    
    # 获取任务日志
    logs = TaskLog.objects.all().order_by('-created_at')
    
    # 分页
    page_number = request.GET.get('page', 1)
    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'logs': page_obj.object_list,
        'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
    }
    
    return render(request, 'tasks/task_management.html', context)


@login_required
def task_logs_api(request):
    """任务日志API"""
    try:
        # 获取参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status = request.GET.get('status', '')
        task_name = request.GET.get('task_name', '')
        
        # 构建查询
        logs = TaskLog.objects.all().order_by('-created_at')
        
        if status:
            logs = logs.filter(status=status)
        if task_name:
            logs = logs.filter(task_name__icontains=task_name)
        
        # 分页
        paginator = Paginator(logs, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        data = []
        for log in page_obj.object_list:
            data.append({
                'id': log.id,
                'task_name': log.task_name,
                'status': log.status,
                'message': log.message,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'execution_time': log.execution_time,
            })
        
        return JsonResponse({
            'status': 'success',
            'data': data,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'current_page': page_obj.number,
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def trigger_dayuan_report(request):
    """手动触发大塬报表发送"""
    try:
        # 异步执行任务
        task = send_daily_dayuan_report.delay()
        
        return JsonResponse({
            'status': 'success',
            'message': '任务已提交执行',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'触发任务失败: {str(e)}'
        }, status=500)


@login_required
def qc_schedule_management(request):
    """QC报表定时发送配置管理页面"""
    from home.utils.permissions import filter_menu_by_permission
    from home.config import MENU_ITEMS
    
    schedules = QCReportSchedule.objects.all().order_by('report_type')
    
    # 初始化默认配置
    if not schedules.exists():
        initialize_default_schedules()
        schedules = QCReportSchedule.objects.all().order_by('report_type')
    
    context = {
        'schedules': schedules,
        'report_types': QCReportSchedule.REPORT_TYPES,
        'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
    }
    return render(request, 'tasks/qc_schedule_management.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_qc_schedule(request):
    """更新QC报表定时发送配置"""
    try:
        data = json.loads(request.body)
        schedule_id = data.get('id')
        
        if schedule_id:
            # 更新现有配置
            schedule = get_object_or_404(QCReportSchedule, id=schedule_id)
        else:
            # 创建新配置
            schedule = QCReportSchedule()
        
        # 更新字段
        schedule.report_type = data.get('report_type')
        schedule.is_enabled = data.get('is_enabled', True)
        schedule.send_hour = int(data.get('send_hour', 8))
        schedule.send_minute = int(data.get('send_minute', 0))
        schedule.recipient_userid = data.get('recipient_userid', '')
        schedule.recipient_name = data.get('recipient_name', '')
        schedule.send_excel = data.get('send_excel', True)
        schedule.send_text = data.get('send_text', True)
        schedule.text_template = data.get('text_template', '')
        
        if not schedule_id:
            schedule.created_by = request.user
        
        schedule.save()
        
        # 自动同步到Celery Beat
        sync_success, sync_message = sync_schedule_to_celery_beat(schedule)
        
        if sync_success:
            message = f'配置保存成功，{sync_message}'
        else:
            message = f'配置保存成功，但{sync_message}'
        
        return JsonResponse({
            'status': 'success',
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'保存失败: {str(e)}'
        })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_qc_schedule(request):
    """删除QC报表定时发送配置"""
    try:
        data = json.loads(request.body)
        schedule_id = data.get('id')
        
        schedule = get_object_or_404(QCReportSchedule, id=schedule_id)
        
        # 删除对应的定时任务
        if schedule.send_hour == 8 and schedule.send_minute == 0:
            task_name = f'qc-report-{schedule.report_type}'
        else:
            task_name = f'qc-report-{schedule.report_type}-{schedule.send_hour:02d}{schedule.send_minute:02d}'
        
        try:
            PeriodicTask.objects.filter(name=task_name).delete()
            sync_message = f'已删除定时任务: {task_name}'
        except Exception as e:
            sync_message = f'删除定时任务失败: {str(e)}'
        
        schedule.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'配置删除成功，{sync_message}'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def toggle_qc_schedule(request):
    """切换QC报表定时发送配置启用状态"""
    try:
        data = json.loads(request.body)
        schedule_id = data.get('id')
        
        schedule = get_object_or_404(QCReportSchedule, id=schedule_id)
        schedule.is_enabled = not schedule.is_enabled
        schedule.save()
        
        # 同步定时任务状态
        sync_success, sync_message = sync_schedule_to_celery_beat(schedule)
        
        status = '启用' if schedule.is_enabled else '禁用'
        if sync_success:
            message = f'配置已{status}，{sync_message}'
        else:
            message = f'配置已{status}，但{sync_message}'
        
        return JsonResponse({
            'status': 'success',
            'message': message,
            'is_enabled': schedule.is_enabled
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'操作失败: {str(e)}'
        })




def initialize_default_schedules():
    """初始化默认的QC报表定时发送配置"""
    default_configs = [
        {
            'report_type': 'dayuan',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 0,
        },
        {
            'report_type': 'dongtai',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 5,
        },
        {
            'report_type': 'changfu',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 10,
        },
        {
            'report_type': 'xinghui',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 15,
        },
        {
            'report_type': 'xinghui2',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 20,
        },
        {
            'report_type': 'yuantong',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 25,
        },
        {
            'report_type': 'yuantong2',
            'recipient_name': 'GaoBieKeLe',
            'recipient_userid': 'GaoBieKeLe',
            'send_hour': 8,
            'send_minute': 30,
        },
    ]
    
    for config in default_configs:
        QCReportSchedule.objects.get_or_create(
            report_type=config['report_type'],
            defaults=config
        )