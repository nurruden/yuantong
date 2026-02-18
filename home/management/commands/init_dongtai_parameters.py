from django.core.management.base import BaseCommand
from home.models import Parameter


class Command(BaseCommand):
    help = '初始化东泰报表的新参数'

    def handle(self, *args, **options):
        # 定义要初始化的参数
        parameters = [
            {
                'id': 'dongtai_sample_weight',
                'name': '东泰样品重量',
                'value': '5',
                'description': '东泰样品重量参数，用于计算',
                'group': '渗透率系数管理'
            },
            {
                'id': 'dongtai_filter_area',
                'name': '东泰过滤面积',
                'value': '3.14',
                'description': '东泰过滤面积参数，用于计算',
                'group': '渗透率系数管理'
            }
        ]

        created_count = 0
        updated_count = 0

        for param_data in parameters:
            param, created = Parameter.objects.get_or_create(
                id=param_data['id'],
                defaults={
                    'name': param_data['name'],
                    'value': param_data['value'],
                    'description': param_data['description'],
                    'group': param_data['group']
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'成功创建参数: {param_data["name"]} = {param_data["value"]}')
                )
            else:
                # 更新现有参数的值和描述
                param.name = param_data['name']
                param.value = param_data['value']
                param.description = param_data['description']
                param.group = param_data['group']
                param.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新参数: {param_data["name"]} = {param_data["value"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'参数初始化完成！创建: {created_count} 个，更新: {updated_count} 个'
            )
        ) 