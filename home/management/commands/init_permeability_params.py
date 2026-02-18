from django.core.management.base import BaseCommand
from home.models import Parameter

class Command(BaseCommand):
    """初始化渗透率系数参数"""
    help = '初始化渗透率系数参数到数据库'

    def handle(self, *args, **options):
        # 定义默认参数
        default_params = [
            {
                'id': 'yuantong_permeability_coefficient',
                'name': '远通渗透率系数',
                'value': '6.4',
                'description': '远通渗透率计算公式中的系数，公式：远通渗透率 = 系数 × 饼厚 × 水粘度 ÷ 过滤时间',
                'group': '渗透率系数'
            },
            {
                'id': 'dongtai_permeability_coefficient',
                'name': '东泰渗透率系数',
                'value': '6.4',
                'description': '东泰渗透率计算公式中的系数，公式：东泰渗透率 = 系数 × 饼厚 × 水粘度 ÷ 过滤时间',
                'group': '渗透率系数'
            },
            {
                'id': 'yuantong_sample_weight',
                'name': '远通样品重量',
                'value': '10.0',
                'description': '远通样品重量参数，用于相关计算',
                'group': '渗透率系数'
            },
            {
                'id': 'dongtai_sample_weight',
                'name': '东泰样品重量',
                'value': '10.0',
                'description': '东泰样品重量参数，用于相关计算',
                'group': '渗透率系数'
            },
            {
                'id': 'yuantong_filter_area',
                'name': '远通过滤面积',
                'value': '28.3',
                'description': '远通过滤面积参数，用于相关计算',
                'group': '渗透率系数'
            },
            {
                'id': 'dongtai_filter_area',
                'name': '东泰过滤面积',
                'value': '28.3',
                'description': '东泰过滤面积参数，用于相关计算',
                'group': '渗透率系数'
            }
        ]

        # 创建或更新参数
        created_count = 0
        updated_count = 0
        
        for param_data in default_params:
            parameter, created = Parameter.objects.get_or_create(
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
                    self.style.SUCCESS(f'✅ 创建参数: {param_data["name"]} = {param_data["value"]}')
                )
            else:
                # 如果参数已存在，可以选择是否更新描述和分组
                if parameter.description != param_data['description'] or parameter.group != param_data['group']:
                    parameter.description = param_data['description']
                    parameter.group = param_data['group']
                    parameter.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'🔄 更新参数: {param_data["name"]} (描述和分组)')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  参数已存在: {param_data["name"]} = {parameter.value}')
                    )

        # 输出总结
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 初始化完成! 创建 {created_count} 个参数，更新 {updated_count} 个参数')
        )
        
        if created_count == 0 and updated_count == 0:
            self.stdout.write(
                self.style.SUCCESS('所有渗透率系数参数都已正确配置 ✨')
            ) 