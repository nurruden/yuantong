# Generated manually to fix UserFavorite model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0031_userprofile_encrypted_password'),
    ]

    operations = [
        # 删除旧字段
        migrations.RemoveField(
            model_name='userfavorite',
            name='page',
        ),
        
        # 设置模型选项
        migrations.AlterModelOptions(
            name='userfavorite',
            options={'ordering': ['-created_at'], 'verbose_name': '用户收藏', 'verbose_name_plural': '用户收藏'},
        ),
        
        # 设置唯一约束
        migrations.AlterUniqueTogether(
            name='userfavorite',
            unique_together={('user', 'favorite_type', 'favorite_id')},
        ),
        
        # 修改其他字段类型
        migrations.AlterField(
            model_name='dayuanqcreport',
            name='sieving_150m',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='+150M (%)'),
        ),
        migrations.AlterField(
            model_name='dayuanqcreport',
            name='sieving_200m',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='+200M (%)'),
        ),
        migrations.AlterField(
            model_name='dayuanqcreport',
            name='sieving_325m',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='+325M (%)'),
        ),
        migrations.AlterField(
            model_name='dongtaiqcreport',
            name='sieving_150m',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='+150M (%)'),
        ),
        migrations.AlterField(
            model_name='dongtaiqcreport',
            name='sieving_200m',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='+200M (%)'),
        ),
        migrations.AlterField(
            model_name='dongtaiqcreport',
            name='sieving_325m',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='+325M (%)'),
        ),
    ] 