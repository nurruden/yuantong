#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信PC端大塬QC报表历史记录显示问题诊断工具
专门诊断为什么企业微信PC端无法显示大塬QC报表历史记录，而手机端可以
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

# 在Django环境设置完成后再导入Django模块
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

def check_wechat_pc_vs_mobile_differences():
    """检查企业微信PC端和手机端的差异"""
    print("🔍 检查企业微信PC端和手机端的差异")
    print("=" * 60)
    
    try:
        from home.views import dayuan_report_history
        
        # 创建请求工厂
        factory = RequestFactory()
        
        # 模拟企业微信PC端的User-Agent
        wechat_pc_user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36 MicroMessenger/8.0.0.1860(0x28000000)'
        
        # 模拟企业微信手机端的User-Agent
        wechat_mobile_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000000) NetType/WIFI Language/zh_CN'
        
        # 获取测试用户
        user = User.objects.filter(username='WangLiMei').first()
        if not user:
            print("❌ 未找到测试用户 WangLiMei")
            return
            
        print(f"✅ 使用测试用户: {user.username} ({user.first_name} {user.last_name})")
        
        # 测试PC端
        print("\n💻 测试企业微信PC端...")
        pc_request = factory.get('/dayuan_report/history/')
        pc_request.META['HTTP_USER_AGENT'] = wechat_pc_user_agent
        pc_request.user = user
        
        try:
            pc_response = dayuan_report_history(pc_request)
            print(f"   ✅ PC端响应状态码: {pc_response.status_code}")
            
            # 检查响应内容
            if hasattr(pc_response, 'content'):
                pc_content = pc_response.content.decode('utf-8')
                print(f"   📄 PC端内容长度: {len(pc_content)}")
                
                # 检查关键元素
                key_elements = [
                    '大塬QC报表',
                    'loadDayuanHistoryData',
                    'exportDayuanReportToExcel',
                    'filterForm',
                    'reportTableBody'
                ]
                
                for element in key_elements:
                    if element in pc_content:
                        print(f"      ✅ PC端包含: {element}")
                    else:
                        print(f"      ❌ PC端不包含: {element}")
                        
        except Exception as e:
            print(f"   ❌ PC端测试失败: {str(e)}")
            
        # 测试手机端
        print("\n📱 测试企业微信手机端...")
        mobile_request = factory.get('/dayuan_report/history/')
        mobile_request.META['HTTP_USER_AGENT'] = wechat_mobile_user_agent
        mobile_request.user = user
        
        try:
            mobile_response = dayuan_report_history(mobile_request)
            print(f"   ✅ 手机端响应状态码: {mobile_response.status_code}")
            
            # 检查响应内容
            if hasattr(mobile_response, 'content'):
                mobile_content = mobile_response.content.decode('utf-8')
                print(f"   📄 手机端内容长度: {len(mobile_content)}")
                
                # 检查关键元素
                for element in key_elements:
                    if element in mobile_content:
                        print(f"      ✅ 手机端包含: {element}")
                    else:
                        print(f"      ❌ 手机端不包含: {element}")
                        
        except Exception as e:
            print(f"   ❌ 手机端测试失败: {str(e)}")
            
        # 比较两个响应
        if 'pc_content' in locals() and 'mobile_content' in locals():
            print("\n🔍 比较PC端和手机端响应...")
            
            if pc_content == mobile_content:
                print("   ✅ PC端和手机端响应内容完全相同")
            else:
                print("   ⚠️  PC端和手机端响应内容不同")
                
                # 检查差异
                pc_lines = pc_content.split('\n')
                mobile_lines = mobile_content.split('\n')
                
                if len(pc_lines) != len(mobile_lines):
                    print(f"      📊 行数差异: PC端 {len(pc_lines)} 行, 手机端 {len(mobile_lines)} 行")
                    
                # 检查JavaScript文件引用差异
                pc_js_files = [line for line in pc_lines if 'dayuan_report.js' in line or 'qc_report_common.js' in line]
                mobile_js_files = [line for line in mobile_lines if 'dayuan_report.js' in line or 'qc_report_common.js' in line]
                
                print(f"      📜 PC端JavaScript引用: {len(pc_js_files)} 个")
                print(f"      📜 手机端JavaScript引用: {len(mobile_js_files)} 个")
                
    except Exception as e:
        print(f"❌ 检查差异失败: {str(e)}")
        import traceback
        traceback.print_exc()

def check_template_rendering_differences():
    """检查模板渲染差异"""
    print("\n📄 检查模板渲染差异...")
    
    try:
        from django.template.loader import render_to_string
        from django.contrib.auth.models import User
        
        # 获取测试用户
        user = User.objects.filter(username='WangLiMei').first()
        if not user:
            print("❌ 未找到测试用户 WangLiMei")
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
        print(f"❌ 检查模板渲染差异失败: {str(e)}")

def check_javascript_execution_environment():
    """检查JavaScript执行环境"""
    print("\n🔧 检查JavaScript执行环境...")
    
    try:
        # 检查是否有针对企业微信PC端的特殊处理
        from home.views import dayuan_report_history
        
        # 创建请求工厂
        factory = RequestFactory()
        
        # 模拟企业微信PC端的请求头
        wechat_pc_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36 MicroMessenger/8.0.0.1860(0x28000000)',
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'HTTP_ACCEPT_LANGUAGE': 'zh-CN,zh;q=0.9,en;q=0.8',
            'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
            'HTTP_CONNECTION': 'keep-alive',
            'HTTP_UPGRADE_INSECURE_REQUESTS': '1'
        }
        
        request = factory.get('/dayuan_report/history/', **wechat_pc_headers)
        
        # 模拟用户登录
        user = User.objects.filter(username='WangLiMei').first()
        if user:
            request.user = user
            
            # 检查请求是否被正确识别
            print(f"   💻 User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')[:50]}...")
            print(f"   🌐 请求路径: {request.path}")
            print(f"   👤 用户: {request.user.username}")
            
            # 检查是否有移动端检测
            is_mobile = any(keyword in request.META.get('HTTP_USER_AGENT', '').lower() 
                           for keyword in ['mobile', 'android', 'iphone', 'ipad'])
            print(f"   📱 是否移动端: {is_mobile}")
            
            # 检查是否是企业微信
            is_wechat = 'micromessenger' in request.META.get('HTTP_USER_AGENT', '').lower()
            print(f"   💬 是否微信: {is_wechat}")
            
            # 检查是否是企业微信PC端
            is_wxwork_pc = 'wxwork' in request.META.get('HTTP_USER_AGENT', '').lower() and not is_mobile
            print(f"   💼 是否企业微信PC端: {is_wxwork_pc}")
            
        else:
            print(f"   ❌ 未找到测试用户 WangLiMei")
            
    except Exception as e:
        print(f"   ❌ 检查JavaScript执行环境失败: {str(e)}")

def check_api_access_differences():
    """检查API访问差异"""
    print("\n🌐 检查API访问差异...")
    
    try:
        from home.views import DayuanQCReportAPI
        
        # 创建请求工厂
        factory = RequestFactory()
        
        # 模拟企业微信PC端的API请求
        wechat_pc_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36 MicroMessenger/8.0.0.1860(0x28000000)',
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            'HTTP_ACCEPT': 'application/json',
            'HTTP_CONTENT_TYPE': 'application/json'
        }
        
        # 模拟企业微信手机端的API请求
        wechat_mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000000) NetType/WIFI Language/zh_CN',
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000000) NetType/WIFI Language/zh_CN',
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            'HTTP_ACCEPT': 'application/json',
            'HTTP_CONTENT_TYPE': 'application/json'
        }
        
        # 获取测试用户
        user = User.objects.filter(username='WangLiMei').first()
        if not user:
            print("❌ 未找到测试用户 WangLiMei")
            return
            
        # 测试PC端API访问
        print("\n💻 测试PC端API访问...")
        pc_request = factory.get('/api/dayuan-report/', **wechat_pc_headers)
        pc_request.user = user
        
        try:
            api_view = DayuanQCReportAPI()
            pc_response = api_view.get(pc_request)
            print(f"   ✅ PC端API响应状态码: {pc_response.status_code}")
            
            if hasattr(pc_response, 'content'):
                pc_content = pc_response.content.decode('utf-8')
                print(f"   📄 PC端API响应内容长度: {len(pc_content)}")
                
                # 检查是否包含数据
                if 'status' in pc_content and 'success' in pc_content:
                    print(f"      ✅ PC端API返回成功状态")
                else:
                    print(f"      ❌ PC端API未返回成功状态")
                    
        except Exception as e:
            print(f"   ❌ PC端API测试失败: {str(e)}")
            
        # 测试手机端API访问
        print("\n📱 测试手机端API访问...")
        mobile_request = factory.get('/api/dayuan-report/', **wechat_mobile_headers)
        mobile_request.user = user
        
        try:
            mobile_response = api_view.get(mobile_request)
            print(f"   ✅ 手机端API响应状态码: {mobile_response.status_code}")
            
            if hasattr(mobile_response, 'content'):
                mobile_content = mobile_response.content.decode('utf-8')
                print(f"   📄 手机端API响应内容长度: {len(mobile_content)}")
                
                # 检查是否包含数据
                if 'status' in mobile_content and 'success' in mobile_content:
                    print(f"      ✅ 手机端API返回成功状态")
                else:
                    print(f"      ❌ 手机端API未返回成功状态")
                    
        except Exception as e:
            print(f"   ❌ 手机端API测试失败: {str(e)}")
            
    except Exception as e:
        print(f"❌ 检查API访问差异失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🔬 企业微信PC端大塬QC报表历史记录显示问题诊断工具")
    print("=" * 80)
    print("🎯 专门诊断为什么企业微信PC端无法显示大塬QC报表历史记录，而手机端可以")
    print("=" * 80)
    
    try:
        # 运行各项检查
        check_wechat_pc_vs_mobile_differences()
        check_template_rendering_differences()
        check_javascript_execution_environment()
        check_api_access_differences()
        
        print("\n" + "=" * 80)
        print("🎯 诊断完成！")
        print("\n📋 可能的问题原因：")
        print("   1. 企业微信PC端和手机端使用了不同的模板")
        print("   2. 企业微信PC端环境下的JavaScript执行受限")
        print("   3. 企业微信PC端有特殊的User-Agent检测逻辑")
        print("   4. 企业微信PC端和手机端的API访问权限不同")
        print("   5. 企业微信PC端有特殊的移动端检测逻辑")
        
        print("\n🔧 建议的解决方案：")
        print("   1. 检查是否有针对企业微信PC端的特殊模板")
        print("   2. 确认企业微信PC端环境下的JavaScript是否正常加载")
        print("   3. 检查是否有针对企业微信PC端的User-Agent检测")
        print("   4. 验证企业微信PC端和手机端的API访问权限是否一致")
        print("   5. 检查是否有针对企业微信PC端的移动端检测逻辑")
        
    except Exception as e:
        print(f"\n❌ 诊断过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
