"""
配置模块
提供系统配置数据，包括菜单配置、QC报表配置等
"""

from .menu_config import MENU_ITEMS, get_wechat_config
from .qc_report_config import (
    QC_REPORT_FIELD_MAPPING,
    QC_REPORT_MODULE_TO_CODE,
    QC_REPORT_MODULE_TO_PERMISSION,
    get_report_module_code,
    get_report_permission_code,
)

__all__ = [
    'MENU_ITEMS',
    'get_wechat_config',
    'QC_REPORT_FIELD_MAPPING',
    'QC_REPORT_MODULE_TO_CODE',
    'QC_REPORT_MODULE_TO_PERMISSION',
    'get_report_module_code',
    'get_report_permission_code',
]
