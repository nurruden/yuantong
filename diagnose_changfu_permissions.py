#!/usr/bin/env python
"""
长富工厂-范春玲权限问题诊断脚本
参考大塬的解决方案来诊断和修复权限问题
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')
django.setup()

from django.contrib.auth.models import User
from system.models import UserRole, RolePermission, Permission, Company, Department, Position, UserProfile
from home.models import MenuPermission, ChangfuQCReport, UserOperationLog
from home.utils import has_hierarchical_permission, get_user_company_department, get_user_data_filter_by_company_department

def diagnose_changfu_user_permissions():
    """诊断长富工厂-范春玲的权限问题"""
    print("🔍 诊断长富工厂-范春玲权限问题")
    print("=" * 60)
    
    # 查找范春玲用户
    users = User.objects.filter(first_name__icontains='范春玲')
    if not users.exists():
        print("❌ 未找到范春玲用户")
        print("正在搜索包含'长富'的用户...")
        users = User.objects.filter(first_name__icontains='长富')
        if not users.exists():
            print("❌ 未找到长富相关用户")
            return
    
    for user in users:
        print(f"\n👤 检查用户: {user.username}")
        print(f"   姓名: {user.first_name} {user.last_name}")
        print(f"   邮箱: {user.email}")
        print(f"   是否超级管理员: {user.is_superuser}")
        print(f"   是否活跃: {user.is_active}")
        
        # 检查用户档案信息
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"\n📋 用户档案信息:")
            print(f"   公司: {profile.company}")
            print(f"   部门: {profile.department}")
            print(f"   职位: {profile.position}")
            print(f"   员工编号: {profile.employee_id}")
        except UserProfile.DoesNotExist:
            print(f"\n⚠️  用户档案不存在 - 这可能是问题的根源！")
        except Exception as e:
            print(f"\n❌ 查询用户档案时出错: {e}")
        
        # 检查用户角色
        print(f"\n🎭 用户角色:")
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        if user_roles.exists():
            for user_role in user_roles:
                print(f"   - {user_role.role.name}")
        else:
            print("   ⚠️  用户没有分配任何角色")
        
        # 检查长富QC报表相关权限
        print(f"\n🔐 长富QC报表权限检查:")
        changfu_permissions = [
            'qc_report_view',
            'changfu_qc_report_view_all',
            'changfu_qc_report_view_company',
            'changfu_qc_report_view_department',
            'changfu_qc_report_view_own',
            'changfu_qc_report_edit',
            'changfu_qc_report_delete'
        ]
        
        for perm_code in changfu_permissions:
            has_perm = has_hierarchical_permission(user, perm_code)
            status = "✅" if has_perm else "❌"
            print(f"   {status} {perm_code}: {has_perm}")
        
        # 检查数据过滤条件
        print(f"\n📊 数据访问权限检查:")
        data_filter = get_user_data_filter_by_company_department(user, '长富QC报表')
        print(f"   数据过滤条件: {data_filter}")
        
        # 检查实际数据访问
        print(f"\n📈 实际数据访问测试:")
        try:
            total_reports = ChangfuQCReport.objects.count()
            print(f"   总报表数量: {total_reports}")
            
            # 应用权限过滤
            from home.utils import apply_company_department_permission_to_queryset
            filtered_reports = apply_company_department_permission_to_queryset(
                ChangfuQCReport.objects.all(), user, '长富QC报表'
            )
            filtered_count = filtered_reports.count()
            print(f"   过滤后报表数量: {filtered_count}")
            
            if filtered_count == 0 and total_reports > 0:
                print("   ⚠️  权限过滤导致无法查看任何数据")
            elif filtered_count == total_reports:
                print("   ✅ 可以查看所有数据")
            else:
                print(f"   ⚠️  只能查看部分数据 ({filtered_count}/{total_reports})")
                
        except Exception as e:
            print(f"   ❌ 数据访问测试失败: {e}")
        
        # 检查操作日志
        print(f"\n📝 操作日志检查:")
        try:
            user_logs = UserOperationLog.objects.filter(username=user.username, report_type='changfu')
            log_count = user_logs.count()
            print(f"   长富QC报表操作记录: {log_count}条")
            
            if log_count > 0:
                recent_logs = user_logs.order_by('-created_at')[:5]
                print("   最近5条操作记录:")
                for log in recent_logs:
                    print(f"     - {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} {log.get_operation_type_display()} {log.operation_detail}")
            else:
                print("   ⚠️  没有找到长富QC报表的操作记录")
                
        except Exception as e:
            print(f"   ❌ 操作日志检查失败: {e}")

def fix_changfu_user_permissions():
    """修复长富工厂-范春玲的权限问题"""
    print("\n🔧 开始修复长富工厂-范春玲权限问题")
    print("=" * 60)
    
    # 查找范春玲用户
    users = User.objects.filter(first_name__icontains='范春玲')
    if not users.exists():
        print("❌ 未找到范春玲用户，无法修复")
        return
    
    for user in users:
        print(f"\n👤 修复用户: {user.username}")
        
        # 1. 检查并创建用户档案
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'CF{user.id:04d}',
                    'is_active': True
                }
            )
            
            if created:
                print("   ✅ 创建了用户档案")
            else:
                print("   ℹ️  用户档案已存在")
            
            # 2. 查找或创建长富公司
            try:
                changfu_company = Company.objects.get(name__icontains='长富')
                print(f"   ✅ 找到长富公司: {changfu_company.name}")
            except Company.DoesNotExist:
                # 创建长富公司
                changfu_company = Company.objects.create(
                    name='长富公司',
                    code='CF',
                    description='长富工厂'
                )
                print("   ✅ 创建了长富公司")
            
            # 3. 查找或创建QC部门
            try:
                qc_department = Department.objects.get(name__icontains='QC', company=changfu_company)
                print(f"   ✅ 找到QC部门: {qc_department.name}")
            except Department.DoesNotExist:
                # 创建QC部门
                qc_department = Department.objects.create(
                    name='QC部门',
                    code='QC',
                    company=changfu_company,
                    description='质量控制部门'
                )
                print("   ✅ 创建了QC部门")
            
            # 4. 查找或创建QC录入员职位
            try:
                qc_position = Position.objects.get(name__icontains='QC录入', company=changfu_company)
                print(f"   ✅ 找到QC录入员职位: {qc_position.name}")
            except Position.DoesNotExist:
                # 创建QC录入员职位
                qc_position = Position.objects.create(
                    name='QC录入员',
                    code='QC_INPUT',
                    company=changfu_company,
                    department=qc_department,
                    description='QC数据录入员'
                )
                print("   ✅ 创建了QC录入员职位")
            
            # 5. 更新用户档案
            profile.company = changfu_company
            profile.department = qc_department
            profile.position = qc_position
            profile.save()
            print("   ✅ 更新了用户档案信息")
            
            # 6. 检查并分配角色权限
            print(f"\n🎭 检查角色权限:")
            
            # 查找长富QC录入角色
            try:
                from system.models import Role
                changfu_role = Role.objects.get(name__icontains='长富QC录入')
                print(f"   ✅ 找到长富QC录入角色: {changfu_role.name}")
            except Role.DoesNotExist:
                # 创建长富QC录入角色
                changfu_role = Role.objects.create(
                    name='长富QC录入员',
                    description='长富工厂QC数据录入角色'
                )
                print("   ✅ 创建了长富QC录入角色")
            
            # 检查用户是否已有该角色
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=changfu_role
            )
            
            if created:
                print("   ✅ 为用户分配了长富QC录入角色")
            else:
                print("   ℹ️  用户已有长富QC录入角色")
            
            # 7. 检查并分配权限
            print(f"\n🔐 检查权限分配:")
            changfu_permissions = [
                ('qc_report_view', 'QC报表查看'),
                ('changfu_qc_report_view_all', '长富QC报表查看全部'),
                ('changfu_qc_report_view_company', '长富QC报表查看公司'),
                ('changfu_qc_report_view_department', '长富QC报表查看部门'),
                ('changfu_qc_report_view_own', '长富QC报表查看自己的'),
                ('changfu_qc_report_edit', '长富QC报表编辑'),
                ('changfu_qc_report_delete', '长富QC报表删除')
            ]
            
            for perm_code, perm_name in changfu_permissions:
                try:
                    permission = Permission.objects.get(code=perm_code)
                    role_perm, created = RolePermission.objects.get_or_create(
                        role=changfu_role,
                        permission=permission
                    )
                    if created:
                        print(f"   ✅ 为角色分配了权限: {perm_name}")
                    else:
                        print(f"   ℹ️  角色已有权限: {perm_name}")
                except Permission.DoesNotExist:
                    print(f"   ⚠️  权限不存在: {perm_code}")
            
            # 8. 验证修复结果
            print(f"\n✅ 验证修复结果:")
            data_filter = get_user_data_filter_by_company_department(user, '长富QC报表')
            print(f"   数据过滤条件: {data_filter}")
            
            total_reports = ChangfuQCReport.objects.count()
            from home.utils import apply_company_department_permission_to_queryset
            filtered_reports = apply_company_department_permission_to_queryset(
                ChangfuQCReport.objects.all(), user, '长富QC报表'
            )
            filtered_count = filtered_reports.count()
            print(f"   总报表数量: {total_reports}")
            print(f"   过滤后报表数量: {filtered_count}")
            
            if filtered_count > 0:
                print("   ✅ 修复成功！用户现在可以查看长富QC报表数据")
            else:
                print("   ⚠️  修复后仍无法查看数据，可能需要进一步检查")
                
        except Exception as e:
            print(f"   ❌ 修复过程中出错: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("🏭 长富工厂-范春玲权限问题诊断和修复工具")
    print("=" * 60)
    
    # 1. 诊断问题
    diagnose_changfu_user_permissions()
    
    # 2. 询问是否修复
    print("\n" + "=" * 60)
    response = input("是否要修复权限问题？(y/n): ").strip().lower()
    
    if response in ['y', 'yes', '是']:
        fix_changfu_user_permissions()
        print("\n🎉 修复完成！请重新测试长富QC报表的历史记录功能。")
    else:
        print("\nℹ️  跳过修复，仅进行诊断。")

if __name__ == '__main__':
    main()
