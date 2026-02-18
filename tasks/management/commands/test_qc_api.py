from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
import json


class Command(BaseCommand):
    help = '测试QC报表定时发送配置API'

    def handle(self, *args, **options):
        self.stdout.write('开始测试QC报表定时发送配置API...')
        
        # 创建测试客户端
        client = Client()
        
        # 获取第一个用户并登录
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('没有找到用户，请先创建用户'))
            return
        
        client.force_login(user)
        
        # 测试数据
        test_data = {
            "id": "",
            "report_type": "dayuan",
            "send_hour": "8",
            "send_minute": "0",
            "recipient_name": "王立梅",
            "recipient_userid": "WangLiMei",
            "send_excel": True,
            "send_text": True,
            "text_template": "",
            "is_enabled": True
        }
        
        # 测试更新配置API
        self.stdout.write('测试更新配置API...')
        try:
            response = client.post(
                '/tasks/api/qc-schedule/update/',
                json.dumps(test_data),
                content_type='application/json'
            )
            
            self.stdout.write(f'状态码: {response.status_code}')
            
            if response.status_code == 200:
                result = response.json()
                self.stdout.write(self.style.SUCCESS(f'API调用成功: {result}'))
            else:
                self.stdout.write(self.style.ERROR(f'API调用失败: {response.content.decode()}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'请求失败: {str(e)}'))
        
        # 测试配置管理页面
        self.stdout.write('测试配置管理页面...')
        try:
            response = client.get('/tasks/qc-schedule/')
            
            self.stdout.write(f'状态码: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('页面访问成功'))
            else:
                self.stdout.write(self.style.ERROR(f'页面访问失败: {response.content.decode()[:200]}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'请求失败: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('API测试完成！'))
