#!/usr/bin/env python
"""
直接配置东泰QC报表跨用户编辑权限的脚本
使用方法：python setup_dongtai_permission.py
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from home.models import Parameter
import json

def setup_dongtai_cross_edit_permission():
    """设置东泰QC报表跨用户编辑权限"""
    
    print("🔧 正在配置东泰QC报表跨用户编辑权限...")
    
    try:
        # 1. 启用跨用户编辑功能
        Parameter.objects.update_or_create(
            id='enable_cross_user_edit',
            defaults={'value': 'true'}
        )
        print("✅ 已启用跨用户编辑功能")
        
        # 2. 为东泰QC报表配置跨用户编辑权限
        permissions = {
            'view': True,
            'edit': True,
            'edit_others': True,  # 关键：允许跨用户编辑
            'delete': True,
            'manage': True
        }
        
        Parameter.objects.update_or_create(
            id='dongtai_qc_report_permissions',
            defaults={'value': json.dumps(permissions)}
        )
        print("✅ 已为东泰QC报表配置跨用户编辑权限")
        
        # 3. 设置编辑期限（可选）
        Parameter.objects.update_or_create(
            id='report_edit_limit',
            defaults={'value': '7'}
        )
        print("✅ 已设置编辑期限为7天")
        
        # 4. 显示当前配置状态
        print("\n📋 当前权限配置状态：")
        
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        cross_edit_status = '✅ 已启用' if cross_edit_param and cross_edit_param.value == 'true' else '❌ 已禁用'
        print(f"   跨用户编辑功能: {cross_edit_status}")
        
        edit_limit_param = Parameter.objects.filter(id='report_edit_limit').first()
        edit_limit = edit_limit_param.value if edit_limit_param else '7'
        print(f"   编辑期限: {edit_limit} 天")
        
        dongtai_param = Parameter.objects.filter(id='dongtai_qc_report_permissions').first()
        if dongtai_param and dongtai_param.value:
            try:
                permissions = json.loads(dongtai_param.value)
                edit_others = '✅ 已启用' if permissions.get('edit_others', False) else '❌ 已禁用'
                print(f"   东泰QC报表跨用户编辑: {edit_others}")
            except:
                print("   东泰QC报表跨用户编辑: ❌ 配置错误")
        else:
            print("   东泰QC报表跨用户编辑: ❌ 未配置")
        
        print("\n🎉 配置完成！现在B用户可以编辑A用户录入的东泰QC报表数据了。")
        print("\n📝 使用说明：")
        print("   1. B用户需要有东泰QC报表的编辑权限")
        print("   2. 数据不能超过编辑期限（默认7天）")
        print("   3. 系统会显示详细的权限说明")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置失败：{str(e)}")
        return False

def check_current_status():
    """检查当前权限状态"""
    print("📊 检查当前权限状态...")
    
    try:
        # 检查跨用户编辑功能
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        cross_edit_enabled = cross_edit_param and cross_edit_param.value == 'true'
        
        # 检查东泰QC报表权限
        dongtai_param = Parameter.objects.filter(id='dongtai_qc_report_permissions').first()
        dongtai_edit_others = False
        if dongtai_param and dongtai_param.value:
            try:
                permissions = json.loads(dongtai_param.value)
                dongtai_edit_others = permissions.get('edit_others', False)
            except:
                pass
        
        # 检查编辑期限
        edit_limit_param = Parameter.objects.filter(id='report_edit_limit').first()
        edit_limit = edit_limit_param.value if edit_limit_param else '7'
        
        print(f"   跨用户编辑功能: {'✅ 已启用' if cross_edit_enabled else '❌ 已禁用'}")
        print(f"   东泰QC报表跨用户编辑: {'✅ 已启用' if dongtai_edit_others else '❌ 已禁用'}")
        print(f"   编辑期限: {edit_limit} 天")
        
        if cross_edit_enabled and dongtai_edit_others:
            print("\n🎉 权限配置正确！B用户可以编辑A用户的数据。")
        else:
            print("\n⚠️  权限配置不完整，需要运行配置脚本。")
            
    except Exception as e:
        print(f"❌ 检查状态失败：{str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_current_status()
    else:
        setup_dongtai_cross_edit_permission()

