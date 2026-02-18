from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from system.models import Role, UserRole


class Command(BaseCommand):
    help = '为现有没有角色的用户自动分配普通用户角色'

    def handle(self, *args, **options):
        self.stdout.write('开始为现有用户分配默认角色...')
        
        # 获取普通用户角色
        normal_role = Role.objects.filter(name='普通用户').first()
        if not normal_role:
            self.stdout.write(
                self.style.ERROR('错误：普通用户角色不存在，请先运行 init_rbac 命令')
            )
            return
        
        # 获取所有没有角色的用户
        users_without_roles = User.objects.exclude(
            id__in=UserRole.objects.values_list('user_id', flat=True)
        )
        
        if not users_without_roles.exists():
            self.stdout.write(
                self.style.SUCCESS('所有用户都已分配角色，无需操作')
            )
            return
        
        # 为没有角色的用户分配普通用户角色
        assigned_count = 0
        for user in users_without_roles:
            try:
                UserRole.objects.create(user=user, role=normal_role)
                self.stdout.write(
                    f'✅ 为用户 {user.username} 分配了普通用户角色'
                )
                assigned_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ 为用户 {user.username} 分配角色失败: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'完成！共为 {assigned_count} 个用户分配了普通用户角色')
        ) 