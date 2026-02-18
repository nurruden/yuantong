#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建可用于「用户名+密码」登录的用户。
会创建 Django User 和 home.models.UserProfile（含 encrypted_password、wechat_id），
登录时前端对密码做 SHA256( SHA256(明文) + salt ) 与后端校验一致。
用法:
  python manage.py create_password_login_user GaoBieKeLe 你的密码
  python manage.py create_password_login_user --username GaoBieKeLe --password 你的密码
"""
import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import UserProfile


class Command(BaseCommand):
    help = '创建或更新可用于密码登录的用户（User + UserProfile.encrypted_password）'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', help='用户名')
        parser.add_argument('password', nargs='?', help='登录密码（明文）')
        parser.add_argument('--username', dest='username_opt', help='用户名')
        parser.add_argument('--password', dest='password_opt', help='登录密码（明文）')

    def handle(self, *args, **options):
        username = options.get('username_opt') or (args[0] if args else None)
        password = options.get('password_opt') or (args[1] if len(args) > 1 else None)
        if not username or not password:
            self.stderr.write('请提供用户名和密码。示例: python manage.py create_password_login_user GaoBieKeLe 你的密码')
            return
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': username,
                'is_staff': True,
                'is_active': True,
            },
        )
        if not created:
            user.is_active = True
            user.save()
        # 与前端一致：后端存储 encrypted_password = SHA256(明文)
        encrypted = hashlib.sha256(password.encode()).hexdigest()
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'encrypted_password': encrypted,
                'wechat_id': user.username,  # 密码登录需 wechat_id 非空，用用户名占位
            },
        )
        if not profile_created:
            profile.encrypted_password = encrypted
            if not profile.wechat_id:
                profile.wechat_id = user.username
            profile.save()
        self.stdout.write(self.style.SUCCESS(f'用户 {username} 已就绪，可使用该用户名和密码在登录页进行密码登录。'))
