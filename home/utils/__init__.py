"""
工具函数模块
提供Excel导出、权限检查、用户信息等辅助函数
"""

from .excel_export import (
    export_production_excel,
    export_qc_report_excel,
    export_qc_report_excel_universal,
)
from .permissions import (
    user_has_permission,
    permission_required,
    system_settings_required,
    has_system_settings_permission,
    filter_menu_by_permission,
)
from .user_helpers import (
    get_user_info,
    is_admin_user,
)

# 从原有的utils.py导入其他函数（保持向后兼容）
# 这些函数暂时保留在home/utils.py中，后续可以考虑移动到utils目录
# 注意：为了避免循环导入，使用importlib直接导入文件
import sys
import os
import importlib.util

# 获取home目录路径
_home_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_utils_py_path = os.path.join(_home_dir, 'utils.py')

# 如果utils.py存在，导入其中的函数
if os.path.exists(_utils_py_path):
    try:
        spec = importlib.util.spec_from_file_location("home.utils_legacy", _utils_py_path)
        utils_legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_legacy)
        
        # 导出常用函数
        can_edit_report = getattr(utils_legacy, 'can_edit_report', None)
        can_delete_report = getattr(utils_legacy, 'can_delete_report', None)
        get_user_data_filter_by_company_department = getattr(utils_legacy, 'get_user_data_filter_by_company_department', None)
        has_hierarchical_permission = getattr(utils_legacy, 'has_hierarchical_permission', None)
        get_user_permission_level = getattr(utils_legacy, 'get_user_permission_level', None)
        get_user_company_department = getattr(utils_legacy, 'get_user_company_department', None)
    except Exception:
        # 如果导入失败，设置为None
        can_edit_report = None
        can_delete_report = None
        get_user_data_filter_by_company_department = None
        has_hierarchical_permission = None
        get_user_permission_level = None
        get_user_company_department = None
else:
    # 如果utils.py不存在，设置为None
    can_edit_report = None
    can_delete_report = None
    get_user_data_filter_by_company_department = None
    has_hierarchical_permission = None
    get_user_permission_level = None
    get_user_company_department = None

__all__ = [
    # Excel导出
    'export_production_excel',
    'export_qc_report_excel',
    'export_qc_report_excel_universal',
    # 权限相关
    'user_has_permission',
    'permission_required',
    'system_settings_required',
    'has_system_settings_permission',
    'filter_menu_by_permission',
    # 用户信息
    'get_user_info',
    'is_admin_user',
    # 从utils.py导入的函数（向后兼容）
    'can_edit_report',
    'can_delete_report',
    'get_user_data_filter_by_company_department',
    'has_hierarchical_permission',
    'get_user_permission_level',
    'get_user_company_department',
]
