from django.contrib.auth.models import AbstractUser
from django.db import models

class WechatUser(AbstractUser):
    wechat_userid = models.CharField(max_length=64, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    avatar = models.URLField(blank=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class Department(models.Model):
    wechat_dept_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    sync_time = models.DateTimeField(auto_now=True)
