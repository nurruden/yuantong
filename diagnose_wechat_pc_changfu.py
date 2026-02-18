#!/usr/bin/env python
"""
企业微信PC端长富QC报表历史记录问题诊断脚本
专门检查企业微信PC端和网页端的差异
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import ChangfuQCReport, UserOperationLog
from home.utils import get_user_data_filter_by_company_department, apply_company_department_permission_to_queryset
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
import json

def simulate_wechat_pc_request():
    """模拟企业微信PC端请求"""
    print("🔍 模拟企业微信PC端请求")
    print("=" * 50)
    
    # 查找范春玲用户
    try:
        user = User.objects.get(username='fanchunling')
        print(f"✅ 找到用户: {user.username}")
        print(f"   姓名: {user.first_name}")
    except User.DoesNotExist:
        print("❌ 未找到范春玲用户")
        return
    
    # 创建模拟请求
    factory = RequestFactory()
    
    # 模拟企业微信PC端的User-Agent
    wechat_pc_headers = {
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 wxwork/1.0.0',
        'HTTP_REFERER': 'https://work.weixin.qq.com/',
        'HTTP_X_FORWARDED_FOR': '127.0.0.1',
        'HTTP_X_REAL_IP': '127.0.0.1'
    }
    
    # 模拟网页端的User-Agent
    web_headers = {
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'HTTP_REFERER': 'https://jilinyuantong.top/',
        'HTTP_X_FORWARDED_FOR': '127.0.0.1',
        'HTTP_X_REAL_IP': '127.0.0.1'
    }
    
    print("\n📱 企业微信PC端请求模拟:")
    wechat_request = factory.get('/changfu_report/history/', **wechat_pc_headers)
    wechat_request.user = user
    
    print(f"   User-Agent: {wechat_request.META.get('HTTP_USER_AGENT', 'N/A')}")
    print(f"   Referer: {wechat_request.META.get('HTTP_REFERER', 'N/A')}")
    print(f"   IP: {wechat_request.META.get('HTTP_X_REAL_IP', 'N/A')}")
    
    print("\n🌐 网页端请求模拟:")
    web_request = factory.get('/changfu_report/history/', **web_headers)
    web_request.user = user
    
    print(f"   User-Agent: {web_request.META.get('HTTP_USER_AGENT', 'N/A')}")
    print(f"   Referer: {web_request.META.get('HTTP_REFERER', 'N/A')}")
    print(f"   IP: {web_request.META.get('HTTP_X_REAL_IP', 'N/A')}")
    
    return wechat_request, web_request

def check_data_access_differences():
    """检查数据访问差异"""
    print("\n📊 检查数据访问差异")
    print("=" * 50)
    
    try:
        user = User.objects.get(username='fanchunling')
    except User.DoesNotExist:
        print("❌ 未找到范春玲用户")
        return
    
    # 检查权限过滤条件
    print(f"\n🔐 权限过滤条件检查:")
    data_filter = get_user_data_filter_by_company_department(user, '长富QC报表')
    print(f"   数据过滤条件: {data_filter}")
    
    # 检查实际数据访问
    print(f"\n📈 数据访问测试:")
    total_reports = ChangfuQCReport.objects.count()
    print(f"   总报表数量: {total_reports}")
    
    # 应用权限过滤
    filtered_reports = apply_company_department_permission_to_queryset(
        ChangfuQCReport.objects.all(), user, '长富QC报表'
    )
    filtered_count = filtered_reports.count()
    print(f"   过滤后报表数量: {filtered_count}")
    
    # 检查最近的数据
    print(f"\n📋 最近的数据记录:")
    recent_reports = filtered_reports.order_by('-created_at')[:5]
    for report in recent_reports:
        print(f"   - {report.date} {report.product_name} (用户: {report.username})")
    
    # 检查用户自己创建的数据
    print(f"\n👤 用户自己创建的数据:")
    own_reports = ChangfuQCReport.objects.filter(username=user.username)
    own_count = own_reports.count()
    print(f"   用户创建的数据数量: {own_count}")
    
    if own_count > 0:
        recent_own = own_reports.order_by('-created_at')[:3]
        for report in recent_own:
            print(f"   - {report.date} {report.product_name}")

def check_operation_logs():
    """检查操作日志"""
    print("\n📝 检查操作日志")
    print("=" * 50)
    
    try:
        user = User.objects.get(username='fanchunling')
    except User.DoesNotExist:
        print("❌ 未找到范春玲用户")
        return
    
    # 检查所有操作日志
    all_logs = UserOperationLog.objects.filter(username=user.username)
    total_logs = all_logs.count()
    print(f"   用户总操作记录: {total_logs}条")
    
    # 检查长富QC报表相关日志
    changfu_logs = UserOperationLog.objects.filter(
        username=user.username, 
        report_type='changfu'
    )
    changfu_count = changfu_logs.count()
    print(f"   长富QC报表操作记录: {changfu_count}条")
    
    # 检查查看历史记录的操作
    view_logs = UserOperationLog.objects.filter(
        username=user.username,
        operation_type='VIEW',
        request_path__icontains='changfu_report'
    )
    view_count = view_logs.count()
    print(f"   查看长富报表记录: {view_count}条")
    
    if view_count > 0:
        print("   最近查看记录:")
        recent_views = view_logs.order_by('-created_at')[:5]
        for log in recent_views:
            print(f"   - {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} {log.request_path}")
            print(f"     User-Agent: {log.user_agent[:100]}...")
    
    # 检查是否有企业微信PC端的访问记录
    wechat_logs = UserOperationLog.objects.filter(
        username=user.username,
        user_agent__icontains='wxwork'
    )
    wechat_count = wechat_logs.count()
    print(f"   企业微信访问记录: {wechat_count}条")
    
    if wechat_count > 0:
        print("   企业微信访问记录:")
        for log in wechat_logs.order_by('-created_at')[:3]:
            print(f"   - {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} {log.operation_type} {log.request_path}")

def check_wechat_pc_specific_issues():
    """检查企业微信PC端特定问题"""
    print("\n🔧 检查企业微信PC端特定问题")
    print("=" * 50)
    
    # 检查长富QC报表的JavaScript文件
    print("\n📄 检查长富QC报表JavaScript文件:")
    
    js_file_path = 'static/js/production/changfu_report.js'
    if os.path.exists(js_file_path):
        print(f"   ✅ 找到JavaScript文件: {js_file_path}")
        
        # 检查是否包含企业微信PC端特殊处理
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'wxwork' in content:
            print("   ✅ 包含企业微信检测代码")
        else:
            print("   ⚠️  未找到企业微信检测代码")
            
        if 'performWeChatWorkExport' in content:
            print("   ✅ 包含企业微信PC端导出处理")
        else:
            print("   ⚠️  未找到企业微信PC端导出处理")
            
        if 'showWeChatPCDownloadPrompt' in content:
            print("   ✅ 包含企业微信PC端下载提示")
        else:
            print("   ⚠️  未找到企业微信PC端下载提示")
    else:
        print(f"   ❌ JavaScript文件不存在: {js_file_path}")
    
    # 检查历史记录模板
    print("\n📄 检查历史记录模板:")
    template_path = 'templates/production/changfu_report_history.html'
    if os.path.exists(template_path):
        print(f"   ✅ 找到模板文件: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'changfu_report.js' in content:
            print("   ✅ 引用了长富QC报表JavaScript文件")
        else:
            print("   ⚠️  未引用长富QC报表JavaScript文件")
    else:
        print(f"   ❌ 模板文件不存在: {template_path}")

def check_session_and_authentication():
    """检查会话和认证问题"""
    print("\n🔐 检查会话和认证问题")
    print("=" * 50)
    
    try:
        user = User.objects.get(username='fanchunling')
    except User.DoesNotExist:
        print("❌ 未找到范春玲用户")
        return
    
    # 检查用户登录状态
    print(f"\n👤 用户认证状态:")
    print(f"   用户ID: {user.id}")
    print(f"   用户名: {user.username}")
    print(f"   是否活跃: {user.is_authenticated}")
    print(f"   最后登录: {user.last_login}")
    
    # 检查用户权限
    print(f"\n🔑 用户权限检查:")
    from home.utils import has_hierarchical_permission
    
    permissions_to_check = [
        'qc_report_view',
        'changfu_qc_report_view_all',
        'changfu_qc_report_view_company',
        'changfu_qc_report_view_department',
        'changfu_qc_report_view_own'
    ]
    
    for perm in permissions_to_check:
        has_perm = has_hierarchical_permission(user, perm)
        status = "✅" if has_perm else "❌"
        print(f"   {status} {perm}: {has_perm}")

def main():
    """主函数"""
    print("🏭 企业微信PC端长富QC报表历史记录问题诊断")
    print("=" * 60)
    
    # 1. 模拟请求
    simulate_wechat_pc_request()
    
    # 2. 检查数据访问差异
    check_data_access_differences()
    
    # 3. 检查操作日志
    check_operation_logs()
    
    # 4. 检查企业微信PC端特定问题
    check_wechat_pc_specific_issues()
    
    # 5. 检查会话和认证
    check_session_and_authentication()
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成！")
    print("\n💡 建议:")
    print("1. 检查企业微信PC端的JavaScript是否正确加载")
    print("2. 确认企业微信PC端的会话状态")
    print("3. 检查是否有企业微信PC端特定的权限限制")
    print("4. 验证操作日志记录功能是否正常工作")

if __name__ == '__main__':
    main()
