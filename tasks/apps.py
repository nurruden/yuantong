from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = '定时任务管理'

    def ready(self):
        """应用启动时调用，用于注册信号处理器"""
        # 导入信号处理器，确保它们被注册
        # 使用 try-except 避免在迁移时出错
        try:
            import tasks.signals  # noqa: F401
        except ImportError:
            pass