#!/usr/bin/env python3
"""
修复QC报表API中的时区显示问题
将所有created_at和updated_at字段从UTC时间转换为东八区时间显示
"""

import re
from django.utils import timezone

def fix_timezone_display():
    """修复时区显示问题"""
    
    # 读取views.py文件
    with open('/var/www/yuantong/home/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复QC报表API中的时间显示
    # 匹配模式：'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'created_at') and report.created_at else '',
    pattern1 = r"'created_at': report\.created_at\.strftime\('%Y-%m-%d %H:%M:%S'\) if hasattr\(report, 'created_at'\) and report\.created_at else '',"
    replacement1 = "'created_at': timezone.localtime(report.created_at).strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'created_at') and report.created_at else '',"
    
    # 匹配模式：'updated_at': report.updated_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'updated_at') and report.updated_at else '',
    pattern2 = r"'updated_at': report\.updated_at\.strftime\('%Y-%m-%d %H:%M:%S'\) if hasattr\(report, 'updated_at'\) and report\.updated_at else '',"
    replacement2 = "'updated_at': timezone.localtime(report.updated_at).strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'updated_at') and report.updated_at else '',"
    
    # 应用替换
    content = re.sub(pattern1, replacement1, content)
    content = re.sub(pattern2, replacement2, content)
    
    # 处理多行的情况
    pattern3 = r"'created_at': report\.created_at\.strftime\('%Y-%m-%d %H:%M:%S'\) if hasattr\(report,\s*'created_at'\) and report\.created_at else '',"
    replacement3 = "'created_at': timezone.localtime(report.created_at).strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'created_at') and report.created_at else '',"
    
    pattern4 = r"'updated_at': report\.updated_at\.strftime\('%Y-%m-%d %H:%M:%S'\) if hasattr\(report,\s*'updated_at'\) and report\.updated_at else '',"
    replacement4 = "'updated_at': timezone.localtime(report.updated_at).strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'updated_at') and report.updated_at else '',"
    
    content = re.sub(pattern3, replacement3, content)
    content = re.sub(pattern4, replacement4, content)
    
    # 写回文件
    with open('/var/www/yuantong/home/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("时区显示修复完成！")
    print("已将所有QC报表API中的created_at和updated_at字段从UTC时间转换为东八区时间显示")

if __name__ == '__main__':
    fix_timezone_display()
