from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_management, name='task_management'),
    path('api/logs/', views.task_logs_api, name='task_logs_api'),
    path('api/trigger-dayuan-report/', views.trigger_dayuan_report, name='trigger_dayuan_report'),
    path('qc-schedule/', views.qc_schedule_management, name='qc_schedule_management'),
    path('api/qc-schedule/update/', views.update_qc_schedule, name='update_qc_schedule'),
    path('api/qc-schedule/delete/', views.delete_qc_schedule, name='delete_qc_schedule'),
    path('api/qc-schedule/toggle/', views.toggle_qc_schedule, name='toggle_qc_schedule'),
]
