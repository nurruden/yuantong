#!/usr/bin/env python
"""
为所有QC报表添加操作日志记录功能
批量处理所有QC报表的JavaScript文件
"""

import os
import re

def add_operation_log_to_qc_report(js_file_path, report_type, report_name):
    """为指定的QC报表添加操作日志记录功能"""
    print(f"🔧 处理 {report_name}: {js_file_path}")
    
    if not os.path.exists(js_file_path):
        print(f"   ❌ 文件不存在: {js_file_path}")
        return False
    
    # 读取文件内容
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有logViewOperation函数
    if 'logViewOperation' in content:
        print(f"   ⚠️  已存在logViewOperation函数，跳过")
        return True
    
    # 查找loadXXXHistoryData函数
    load_function_pattern = rf'async function load{report_type.capitalize()}HistoryData'
    if not re.search(load_function_pattern, content):
        print(f"   ❌ 未找到load{report_type.capitalize()}HistoryData函数")
        return False
    
    # 查找成功加载数据的位置
    success_pattern = r'if \(result\.status === \'success\'\) \{'
    if not re.search(success_pattern, content):
        print(f"   ❌ 未找到成功状态检查")
        return False
    
    # 在成功加载数据后添加操作日志记录
    display_pattern = rf'display{report_type.capitalize()}HistoryData\(result\.data\)'
    if not re.search(display_pattern, content):
        print(f"   ❌ 未找到display函数调用")
        return False
    
    # 添加操作日志记录代码
    log_code = f'''
                // 记录查看操作日志（仅在第一次加载或页面变化时记录）
                if (page === 1) {{
                    logViewOperation();
                }}
                
'''
    
    # 在display函数调用后添加操作日志记录
    new_content = re.sub(
        rf'({display_pattern});',
        rf'\1;{log_code}',
        content
    )
    
    # 在文件末尾添加logViewOperation函数
    log_function = f'''

// 记录查看操作日志
async function logViewOperation() {{
    try {{
        const response = await fetch('/api/log-view-operation/', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }},
            body: JSON.stringify({{
                report_type: '{report_type}',
                operation_type: 'VIEW',
                operation_detail: '查看{report_name}历史记录',
                request_path: window.location.pathname
            }})
        }});
        
        if (response.ok) {{
            console.log('✅ 查看操作日志记录成功');
        }} else {{
            console.warn('⚠️ 查看操作日志记录失败:', response.status);
        }}
    }} catch (error) {{
        console.warn('⚠️ 查看操作日志记录异常:', error);
    }}
}}
'''
    
    new_content += log_function
    
    # 写回文件
    with open(js_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✅ 成功添加操作日志记录功能")
    return True

def main():
    """主函数"""
    print("🏭 为所有QC报表添加操作日志记录功能")
    print("=" * 60)
    
    # QC报表配置
    qc_reports = [
        {
            'js_file': 'static/js/production/xinghui_report.js',
            'report_type': 'xinghui',
            'report_name': '兴辉QC报表'
        },
        {
            'js_file': 'static/js/production/xinghui2_report.js',
            'report_type': 'xinghui2',
            'report_name': '兴辉二线QC报表'
        },
        {
            'js_file': 'static/js/production/yuantong_report.js',
            'report_type': 'yuantong',
            'report_name': '远通QC报表'
        },
        {
            'js_file': 'static/js/production/yuantong2_report.js',
            'report_type': 'yuantong2',
            'report_name': '远通二线QC报表'
        }
    ]
    
    success_count = 0
    total_count = len(qc_reports)
    
    for report in qc_reports:
        if add_operation_log_to_qc_report(
            report['js_file'], 
            report['report_type'], 
            report['report_name']
        ):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 处理完成: {success_count}/{total_count} 个QC报表")
    
    if success_count == total_count:
        print("✅ 所有QC报表都已添加操作日志记录功能")
    else:
        print(f"⚠️  有 {total_count - success_count} 个QC报表处理失败")
    
    print("\n💡 注意事项:")
    print("1. 东泰QC报表和长富QC报表已经手动处理完成")
    print("2. 大塬QC报表已经手动处理完成")
    print("3. 其他QC报表已通过脚本批量处理")
    print("4. 请测试所有QC报表的操作日志记录功能")

if __name__ == '__main__':
    main()

