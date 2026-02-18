#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信应用大塬QC报表访问问题诊断工具
专门诊断为什么企业微信应用无法查看大塬QC报表历史记录
"""

import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.middleware.common import CommonMiddleware
from django.middleware.security import SecurityMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

def check_wechat_enterprise_specific_issues():
    """检查企业微信应用特有的问题"""
    print("🔍 检查企业微信应用特有问题")
    print("=" * 60)
    
    # 1. 检查User-Agent处理
    print("\n📱 检查User-Agent处理...")
    try:
        from home.views import dayuan_report_history
        
        # 模拟企业微信的User-Agent
        wechat_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000000) NetType/WIFI Language/zh_CN',
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 MicroMessenger/8.0.0.1860(0x28000000)',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36 MicroMessenger/8.0.0.1860(0x28000000)'
        ]
        
        factory = RequestFactory()
        for i, user_agent in enumerate(wechat_user_agents, 1):
            request = factory.get('/dayuan_report/history/')
            request.META['HTTP_USER_AGENT'] = user_agent
            request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'  # 模拟AJAX请求
            
            print(f"   📱 测试User-Agent {i}: {user_agent[:50]}...")
            
            try:
                # 模拟用户登录
                user = User.objects.filter(username='yyz').first()
                if user:
                    request.user = user
                    
                    # 检查视图是否正常响应
                    response = dayuan_report_history(request)
                    print(f"      ✅ 响应状态码: {response.status_code}")
                    
                    # 检查响应内容
                    if hasattr(response, 'content'):
                        content = response.content.decode('utf-8')
                        if '大塬QC报表' in content:
                            print(f"      ✅ 页面内容包含'大塬QC报表'")
                        else:
                            print(f"      ⚠️  页面内容不包含'大塬QC报表'")
                            
                        # 检查JavaScript文件引用
                        js_files = ['dayuan_report.js', 'qc_report_common.js']
                        for js_file in js_files:
                            if js_file in content:
                                print(f"      ✅ 引用了 {js_file}")
                            else:
                                print(f"      ❌ 未引用 {js_file}")
                                
                else:
                    print(f"      ❌ 未找到测试用户 yyz")
                    
            except Exception as e:
                print(f"      ❌ 测试失败: {str(e)}")
                
    except Exception as e:
        print(f"   ❌ 检查User-Agent处理失败: {str(e)}")

def check_mobile_specific_features():
    """检查移动端特有功能"""
    print("\n📱 检查移动端特有功能...")
    
    try:
        # 检查是否有移动端专用的视图或模板
        from django.template.loader import get_template
        
        mobile_templates = [
            'production/dayuan_report_history_mobile.html',
            'production/dayuan_report_history_wechat.html',
            'production/dayuan_report_history.html'
        ]
        
        for template_name in mobile_templates:
            try:
                template = get_template(template_name)
                print(f"   ✅ 模板 {template_name} 存在")
                
                # 检查模板内容
                template_content = template.template.source
                if '大塬QC报表' in template_content:
                    print(f"      ✅ 模板包含'大塬QC报表'")
                if 'loadDayuanHistoryData' in template_content:
                    print(f"      ✅ 模板包含JavaScript函数")
                    
            except Exception as e:
                print(f"   ❌ 模板 {template_name} 不存在或无法加载: {str(e)}")
                
    except Exception as e:
        print(f"   ❌ 检查移动端功能失败: {str(e)}")

def check_wechat_enterprise_integration():
    """检查企业微信集成相关配置"""
    print("\n🏢 检查企业微信集成配置...")
    
    try:
        # 检查settings中是否有企业微信相关配置
        wechat_settings = [
            'WECHAT_ENTERPRISE_APP_ID',
            'WECHAT_ENTERPRISE_SECRET',
            'WECHAT_ENTERPRISE_AGENT_ID',
            'WECHAT_ENTERPRISE_CORP_ID'
        ]
        
        for setting_name in wechat_settings:
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                if value:
                    print(f"   ✅ {setting_name}: 已配置")
                else:
                    print(f"   ⚠️  {setting_name}: 配置为空")
            else:
                print(f"   ❌ {setting_name}: 未配置")
                
        # 检查是否有企业微信相关的中间件
        wechat_middleware = [
            'wechat.middleware.WeChatMiddleware',
            'wechat_enterprise.middleware.WeChatEnterpriseMiddleware'
        ]
        
        for middleware in wechat_middleware:
            if middleware in settings.MIDDLEWARE:
                print(f"   ✅ 中间件 {middleware} 已启用")
            else:
                print(f"   ❌ 中间件 {middleware} 未启用")
                
    except Exception as e:
        print(f"   ❌ 检查企业微信集成失败: {str(e)}")

def check_mobile_optimization():
    """检查移动端优化配置"""
    print("\n📱 检查移动端优化配置...")
    
    try:
        # 检查是否有移动端检测
        from django.middleware.common import CommonMiddleware
        
        # 检查模板标签
        from django.template.defaulttags import register
        
        # 检查是否有移动端检测的模板标签
        mobile_detection_tags = [
            'is_mobile',
            'is_wechat',
            'is_wechat_enterprise',
            'mobile_optimized'
        ]
        
        for tag_name in mobile_detection_tags:
            try:
                # 尝试获取模板标签
                tag = register.tags.get(tag_name)
                if tag:
                    print(f"   ✅ 模板标签 {tag_name} 可用")
                else:
                    print(f"   ❌ 模板标签 {tag_name} 不可用")
            except:
                print(f"   ❌ 模板标签 {tag_name} 检查失败")
                
        # 检查CSS和JS文件是否针对移动端优化
        static_files = [
            'css/mobile.css',
            'css/wechat.css',
            'js/mobile.js',
            'js/wechat.js'
        ]
        
        for static_file in static_files:
            static_path = os.path.join(settings.STATIC_ROOT, static_file)
            if os.path.exists(static_path):
                print(f"   ✅ 静态文件 {static_file} 存在")
            else:
                print(f"   ❌ 静态文件 {static_file} 不存在")
                
    except Exception as e:
        print(f"   ❌ 检查移动端优化失败: {str(e)}")

def check_wechat_enterprise_user_agent():
    """检查企业微信User-Agent的特殊处理"""
    print("\n🔍 检查企业微信User-Agent特殊处理...")
    
    try:
        # 检查是否有针对企业微信的特殊处理逻辑
        from home.views import dayuan_report_history
        
        # 创建请求工厂
        factory = RequestFactory()
        
        # 模拟企业微信的请求头
        wechat_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000000) NetType/WIFI Language/zh_CN',
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'HTTP_ACCEPT_LANGUAGE': 'zh-CN,zh;q=0.9,en;q=0.8',
            'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
            'HTTP_CONNECTION': 'keep-alive',
            'HTTP_UPGRADE_INSECURE_REQUESTS': '1'
        }
        
        request = factory.get('/dayuan_report/history/', **wechat_headers)
        
        # 模拟用户登录
        user = User.objects.filter(username='yyz').first()
        if user:
            request.user = user
            
            # 检查请求是否被正确识别
            print(f"   📱 User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')[:50]}...")
            print(f"   🌐 请求路径: {request.path}")
            print(f"   👤 用户: {request.user.username}")
            
            # 检查是否有移动端检测
            is_mobile = any(keyword in request.META.get('HTTP_USER_AGENT', '').lower() 
                           for keyword in ['mobile', 'android', 'iphone', 'ipad'])
            print(f"   📱 是否移动端: {is_mobile}")
            
            # 检查是否是企业微信
            is_wechat = 'micromessenger' in request.META.get('HTTP_USER_AGENT', '').lower()
            print(f"   💬 是否微信: {is_wechat}")
            
        else:
            print(f"   ❌ 未找到测试用户 yyz")
            
    except Exception as e:
        print(f"   ❌ 检查企业微信User-Agent失败: {str(e)}")

def check_template_rendering_differences():
    """检查模板渲染差异"""
    print("\n📄 检查模板渲染差异...")
    
    try:
        from django.template.loader import render_to_string
        from django.contrib.auth.models import User
        
        # 获取测试用户
        user = User.objects.filter(username='yyz').first()
        if not user:
            print("   ❌ 未找到测试用户 yyz")
            return
            
        # 创建上下文
        context = {
            'user': user,
            'request': None
        }
        
        # 尝试渲染模板
        try:
            template_content = render_to_string('production/dayuan_report_history.html', context)
            print(f"   ✅ 模板渲染成功，内容长度: {len(template_content)}")
            
            # 检查关键内容
            key_elements = [
                '大塬QC报表',
                'loadDayuanHistoryData',
                'exportDayuanReportToExcel',
                'filterForm',
                'reportTableBody'
            ]
            
            for element in key_elements:
                if element in template_content:
                    print(f"      ✅ 包含: {element}")
                else:
                    print(f"      ❌ 不包含: {element}")
                    
        except Exception as e:
            print(f"   ❌ 模板渲染失败: {str(e)}")
            
    except Exception as e:
        print(f"   ❌ 检查模板渲染差异失败: {str(e)}")

def main():
    """主函数"""
    print("🔬 企业微信应用大塬QC报表访问问题诊断工具")
    print("=" * 80)
    print("🎯 专门诊断为什么企业微信应用无法查看大塬QC报表历史记录")
    print("=" * 80)
    
    try:
        # 运行各项检查
        check_wechat_enterprise_specific_issues()
        check_mobile_specific_features()
        check_wechat_enterprise_integration()
        check_mobile_optimization()
        check_wechat_enterprise_user_agent()
        check_template_rendering_differences()
        
        print("\n" + "=" * 80)
        print("🎯 诊断完成！")
        print("\n📋 可能的问题原因：")
        print("   1. 企业微信应用使用了不同的模板或视图")
        print("   2. 企业微信环境下的JavaScript执行受限")
        print("   3. 移动端优化导致功能缺失")
        print("   4. 企业微信集成配置问题")
        print("   5. User-Agent检测导致功能降级")
        
        print("\n🔧 建议的解决方案：")
        print("   1. 检查企业微信应用是否使用了专门的移动端模板")
        print("   2. 确认企业微信环境下的JavaScript是否正常加载")
        print("   3. 检查是否有针对企业微信的特殊处理逻辑")
        print("   4. 验证移动端优化是否过度简化了功能")
        
    except Exception as e:
        print(f"\n❌ 诊断过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()


