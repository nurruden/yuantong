#!/usr/bin/env python
"""
修复大塬QC报表时间字段导入问题
重新导入正确的时间数据
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime, date, time

# 设置Django环境
sys.path.append('/var/www/yuantong')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from home.models import DayuanQCReport
from django.contrib.auth.models import User as AuthUser

def fix_time_import():
    """修复时间字段导入问题"""
    print("🔧 修复大塬QC报表时间字段导入问题")
    print("=" * 60)
    
    # 读取Excel文件
    excel_file = "dayuanqc.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ 文件不存在: {excel_file}")
        return
    
    print(f"📄 读取Excel文件: {excel_file}")
    df = pd.read_excel(excel_file)
    print(f"📊 数据行数: {len(df)}")
    
    # 获取用户
    try:
        user = AuthUser.objects.get(username="GaoBieKeLe")
    except AuthUser.DoesNotExist:
        print("❌ 用户不存在")
        return
    
    # 删除之前导入的2025-09-08和2025-09-09的数据
    print("\n🗑️ 删除之前导入的2025-09-08和2025-09-09数据...")
    deleted_count = DayuanQCReport.objects.filter(
        date__in=['2025-09-08', '2025-09-09'],
        username="GaoBieKeLe"
    ).delete()[0]
    print(f"✅ 删除了 {deleted_count} 条记录")
    
    # 重新导入数据
    print("\n🚀 重新导入数据...")
    imported_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            # 创建数据字典
            data = {}
            
            # 处理日期
            if 'date' in row and pd.notna(row['date']):
                if isinstance(row['date'], str):
                    data['date'] = datetime.strptime(row['date'], '%Y-%m-%d').date()
                else:
                    data['date'] = row['date'].date()
            else:
                data['date'] = date.today()
            
            # 处理时间 - 修复版本
            if 'time' in row and pd.notna(row['time']):
                if isinstance(row['time'], str):
                    try:
                        data['time'] = datetime.strptime(row['time'], '%H:%M').time()
                    except ValueError:
                        try:
                            data['time'] = datetime.strptime(row['time'], '%H:%M:%S').time()
                        except ValueError:
                            data['time'] = time(0, 0)
                elif isinstance(row['time'], time):
                    # 如果已经是time对象，直接使用
                    data['time'] = row['time']
                elif hasattr(row['time'], 'time'):
                    # 如果是有time方法的对象，调用time()方法
                    data['time'] = row['time'].time()
                else:
                    data['time'] = time(0, 0)
            else:
                data['time'] = time(0, 0)
            
            # 处理字符串字段
            string_fields = ['shift', 'product_name', 'packaging', 'batch_number', 'flux', 'remarks']
            for field in string_fields:
                if field in row and pd.notna(row[field]):
                    data[field] = str(row[field])
                else:
                    data[field] = ''
            
            # 处理数字字段
            numeric_fields = [
                'moisture_after_drying', 'alkali_content', 'permeability', 'permeability_long',
                'wet_cake_density', 'bulk_density', 'brightness', 'swirl', 'odor',
                'conductance', 'ph', 'moisture', 'bags', 'tons', 'fe_ion', 'ca_ion',
                'al_ion', 'oil_absorption', 'water_absorption', 'sieving_14m', 'sieving_30m',
                'sieving_40m', 'sieving_80m'
            ]
            
            for field in numeric_fields:
                if field in row and pd.notna(row[field]):
                    try:
                        data[field] = float(row[field])
                    except (ValueError, TypeError):
                        data[field] = None
                else:
                    data[field] = None
            
            # 处理筛分字段（可能是字符串）
            sieving_fields = ['sieving_100m', 'sieving_150m', 'sieving_200m', 'sieving_325m']
            for field in sieving_fields:
                if field in row and pd.notna(row[field]):
                    data[field] = str(row[field])
                else:
                    data[field] = ''
            
            # 设置用户信息
            data['user'] = user
            data['username'] = user.username
            
            # 创建记录
            report = DayuanQCReport.objects.create(**data)
            imported_count += 1
            
            print(f"✅ 第 {index + 1} 条: {report.date} {report.time} - {report.product_name} - {report.batch_number}")
            
        except Exception as e:
            error_count += 1
            print(f"❌ 第 {index + 1} 条导入失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 修复完成!")
    print(f"✅ 成功导入: {imported_count} 条")
    print(f"❌ 导入失败: {error_count} 条")
    
    # 验证修复结果
    print(f"\n🔍 验证修复结果:")
    recent_records = DayuanQCReport.objects.filter(
        date__in=['2025-10-06', '2025-10-08']
    ).order_by('date', 'time')[:10]
    
    for i, record in enumerate(recent_records, 1):
        print(f"  {i}. {record.date} {record.time} - {record.product_name} - {record.batch_number}")

if __name__ == "__main__":
    fix_time_import()
