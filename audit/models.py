from django.db import models
from django.conf import settings

class OperationLog(models.Model):
    ACTION_CHOICES = [('LOGIN','登录'),('SYNC','同步')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
