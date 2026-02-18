# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='encrypted_password',
            field=models.CharField(blank=True, help_text='用于用户名密码登录验证的加密密码', max_length=255, null=True, verbose_name='加密密码'),
        ),
    ] 