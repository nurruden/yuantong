from django.core.management.base import BaseCommand
from home.models import Parameter

class Command(BaseCommand):
    """删除渗透率系数参数"""
    help = '删除长富渗透率偏移量和饼密度计算系数参数'

    def handle(self, *args, **options):
        # 要删除的参数ID列表
        params_to_remove = [
            'changfu_permeability_offset',
            'cake_density_coefficient'
        ]

        removed_count = 0
        
        for param_id in params_to_remove:
            try:
                parameter = Parameter.objects.get(id=param_id)
                parameter.delete()
                removed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 删除参数: {param_id}')
                )
            except Parameter.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  参数不存在: {param_id}')
                )

        # 输出总结
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 删除完成! 共删除 {removed_count} 个参数')
        )
        
        if removed_count == 0:
            self.stdout.write(
                self.style.SUCCESS('没有需要删除的参数 ✨')
            ) 