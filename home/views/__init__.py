"""
Views模块
将views.py拆分为多个子模块以提高可维护性
"""

# 导入QC报表相关的类和函数
# 注意：必须分两次导入，先导入类，再导入函数，避免函数覆盖类
# 第一次导入：只导入API类，并保存到临时变量
import home.views.qc_reports as _qc_reports_module

# 保存API类到模块级别的变量（避免被后续导入覆盖）
BaseQCReportAPI = _qc_reports_module.BaseQCReportAPI
DayuanQCReportAPI = _qc_reports_module.DayuanQCReportAPI
DongtaiQCReportAPI = _qc_reports_module.DongtaiQCReportAPI
YuantongQCReportAPI = _qc_reports_module.YuantongQCReportAPI
Yuantong2QCReportAPI = _qc_reports_module.Yuantong2QCReportAPI
XinghuiQCReportAPI = _qc_reports_module.XinghuiQCReportAPI
ChangfuQCReportAPI = _qc_reports_module.ChangfuQCReportAPI
Xinghui2QCReportAPI = _qc_reports_module.Xinghui2QCReportAPI

# 第二次导入：导入所有报表视图函数和导出函数
# 注意：这些函数不会覆盖已保存的类变量
qc_report = _qc_reports_module.qc_report
dayuan_report = _qc_reports_module.dayuan_report
dongtai_report = _qc_reports_module.dongtai_report
yuantong_report = _qc_reports_module.yuantong_report
yuantong2_report = _qc_reports_module.yuantong2_report
xinghui_report = _qc_reports_module.xinghui_report
xinghui2_report = _qc_reports_module.xinghui2_report
changfu_report = _qc_reports_module.changfu_report
dayuan_report_edit = _qc_reports_module.dayuan_report_edit
dayuan_report_history = _qc_reports_module.dayuan_report_history
dayuan_report_import_excel = _qc_reports_module.dayuan_report_import_excel
dayuan_report_download_template = _qc_reports_module.dayuan_report_download_template
dongtai_report_edit = _qc_reports_module.dongtai_report_edit
dongtai_report_history = _qc_reports_module.dongtai_report_history
dongtai_report_import_excel = _qc_reports_module.dongtai_report_import_excel
dongtai_report_download_template = _qc_reports_module.dongtai_report_download_template
yuantong_report_edit = _qc_reports_module.yuantong_report_edit
yuantong_report_history = _qc_reports_module.yuantong_report_history
yuantong_report_import_excel = _qc_reports_module.yuantong_report_import_excel
yuantong_report_download_template = _qc_reports_module.yuantong_report_download_template
yuantong2_report_edit = _qc_reports_module.yuantong2_report_edit
yuantong2_report_history = _qc_reports_module.yuantong2_report_history
yuantong2_report_import_excel = _qc_reports_module.yuantong2_report_import_excel
yuantong2_report_download_template = _qc_reports_module.yuantong2_report_download_template
xinghui_report_edit = _qc_reports_module.xinghui_report_edit
xinghui_report_history = _qc_reports_module.xinghui_report_history
xinghui_report_import_excel = _qc_reports_module.xinghui_report_import_excel
xinghui_report_download_template = _qc_reports_module.xinghui_report_download_template
xinghui2_report_edit = _qc_reports_module.xinghui2_report_edit
xinghui2_report_history = _qc_reports_module.xinghui2_report_history
xinghui2_report_import_excel = _qc_reports_module.xinghui2_report_import_excel
xinghui2_report_download_template = _qc_reports_module.xinghui2_report_download_template
changfu_report_edit = _qc_reports_module.changfu_report_edit
changfu_report_history = _qc_reports_module.changfu_report_history
changfu_report_import_excel = _qc_reports_module.changfu_report_import_excel
changfu_report_download_template = _qc_reports_module.changfu_report_download_template
export_dongtai_report_excel = _qc_reports_module.export_dongtai_report_excel
export_dongtai_yesterday_production = _qc_reports_module.export_dongtai_yesterday_production
export_dongtai_today_production = _qc_reports_module.export_dongtai_today_production
export_dayuan_report_excel = _qc_reports_module.export_dayuan_report_excel
export_dayuan_yesterday_production = _qc_reports_module.export_dayuan_yesterday_production
export_dayuan_today_production = _qc_reports_module.export_dayuan_today_production
export_yuantong_report_excel = _qc_reports_module.export_yuantong_report_excel
export_yuantong_yesterday_production = _qc_reports_module.export_yuantong_yesterday_production
export_yuantong_today_production = _qc_reports_module.export_yuantong_today_production
export_yuantong2_report_excel = _qc_reports_module.export_yuantong2_report_excel
export_yuantong2_yesterday_production = _qc_reports_module.export_yuantong2_yesterday_production
export_yuantong2_today_production = _qc_reports_module.export_yuantong2_today_production
export_xinghui_report_excel = _qc_reports_module.export_xinghui_report_excel
export_xinghui_yesterday_production = _qc_reports_module.export_xinghui_yesterday_production
export_xinghui_today_production = _qc_reports_module.export_xinghui_today_production
export_changfu_report_excel = _qc_reports_module.export_changfu_report_excel
export_changfu_yesterday_production = _qc_reports_module.export_changfu_yesterday_production
export_changfu_today_production = _qc_reports_module.export_changfu_today_production
export_xinghui2_report_excel = _qc_reports_module.export_xinghui2_report_excel
export_xinghui2_yesterday_production = _qc_reports_module.export_xinghui2_yesterday_production
export_xinghui2_today_production = _qc_reports_module.export_xinghui2_today_production

# 导入微信认证相关的类和函数
from .wechat_auth import (
    WeChatUserListAPI,
    WeChatCallbackView,
    WeChatMessageReceiveView,
    wechat_login,
    custom_logout,
)

# 注意：其他视图仍然在home/views.py中
# 为了避免循环导入，urls.py应该直接从home.views导入其他视图
# 这里只导出QC报表和微信认证相关的视图

# 从主views.py导入其他常用的类和函数
# 使用__getattr__来延迟导入，避免循环导入问题
import sys
import os

_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_views_py_path = os.path.join(_parent_dir, 'views.py')
_views_main_cache = None

def _get_views_main():
    """获取主views.py模块（延迟加载）"""
    global _views_main_cache
    if _views_main_cache is None and os.path.exists(_views_py_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("home.views_main", _views_py_path)
        _views_main_cache = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_views_main_cache)
    return _views_main_cache

def __getattr__(name):
    """延迟导入views.py中的其他函数和类"""
    views_main = _get_views_main()
    if views_main and hasattr(views_main, name):
        return getattr(views_main, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# 预加载常用视图类（避免每次都调用__getattr__）
try:
    views_main = _get_views_main()
    if views_main:
        PermissionAPI = getattr(views_main, 'PermissionAPI', None)
        HomeView = getattr(views_main, 'HomeView', None)
        IndexView = getattr(views_main, 'IndexView', None)
        ParameterConfigView = getattr(views_main, 'ParameterConfigView', None)
        ProductionHistoryView = getattr(views_main, 'ProductionHistoryView', None)
        PasswordLoginAPI = getattr(views_main, 'PasswordLoginAPI', None)
        RawSoilStorageView = getattr(views_main, 'RawSoilStorageView', None)
        UserManagementAPI = getattr(views_main, 'UserManagementAPI', None)
        UserPasswordResetAPI = getattr(views_main, 'UserPasswordResetAPI', None)
        RBACRoleAPI = getattr(views_main, 'RBACRoleAPI', None)
        RBACPermissionAPI = getattr(views_main, 'RBACPermissionAPI', None)
        RBACUserRoleAPI = getattr(views_main, 'RBACUserRoleAPI', None)
        RBACRolePermissionAPI = getattr(views_main, 'RBACRolePermissionAPI', None)
        rbac_management = getattr(views_main, 'rbac_management', None)
        get_parameter = getattr(views_main, 'get_parameter', None)
        InventoryOrgAPI = getattr(views_main, 'InventoryOrgAPI', None)
        MaterialMappingAPI = getattr(views_main, 'MaterialMappingAPI', None)
        WarehouseMappingAPI = getattr(views_main, 'WarehouseMappingAPI', None)
        CostCenterMappingAPI = getattr(views_main, 'CostCenterMappingAPI', None)
        CostObjectMappingAPI = getattr(views_main, 'CostObjectMappingAPI', None)
        WaterDeductionRateAPI = getattr(views_main, 'WaterDeductionRateAPI', None)
        OperationObjectAPI = getattr(views_main, 'OperationObjectAPI', None)
        ProductModelAPI = getattr(views_main, 'ProductModelAPI', None)
        PackagingAPI = getattr(views_main, 'PackagingAPI', None)
        UserFavoriteAPI = getattr(views_main, 'UserFavoriteAPI', None)
except:
    PermissionAPI = None
    HomeView = None
    IndexView = None
    ParameterConfigView = None
    ProductionHistoryView = None
    PasswordLoginAPI = None
    RawSoilStorageView = None
    UserManagementAPI = None
    UserPasswordResetAPI = None
    RBACRoleAPI = None
    RBACPermissionAPI = None
    RBACUserRoleAPI = None
    RBACRolePermissionAPI = None
    rbac_management = None
    get_parameter = None
    InventoryOrgAPI = None
    MaterialMappingAPI = None
    WarehouseMappingAPI = None
    CostCenterMappingAPI = None
    CostObjectMappingAPI = None
    WaterDeductionRateAPI = None
    OperationObjectAPI = None
    ProductModelAPI = None
    PackagingAPI = None
    UserFavoriteAPI = None

__all__ = [
    # QC报表API
    'BaseQCReportAPI',
    'DayuanQCReportAPI',
    'DongtaiQCReportAPI',
    'YuantongQCReportAPI',
    'Yuantong2QCReportAPI',
    'XinghuiQCReportAPI',
    'ChangfuQCReportAPI',
    'Xinghui2QCReportAPI',
    # QC报表视图函数
    'qc_report', 'dayuan_report', 'dongtai_report', 'yuantong_report', 'yuantong2_report',
    'xinghui_report', 'xinghui2_report', 'changfu_report',
    'dayuan_report_edit', 'dayuan_report_history', 'dayuan_report_import_excel', 'dayuan_report_download_template',
    'dongtai_report_edit', 'dongtai_report_history', 'dongtai_report_import_excel', 'dongtai_report_download_template',
    'yuantong_report_edit', 'yuantong_report_history', 'yuantong_report_import_excel', 'yuantong_report_download_template',
    'yuantong2_report_edit', 'yuantong2_report_history', 'yuantong2_report_import_excel', 'yuantong2_report_download_template',
    'xinghui_report_edit', 'xinghui_report_history', 'xinghui_report_import_excel', 'xinghui_report_download_template',
    'xinghui2_report_edit', 'xinghui2_report_history', 'xinghui2_report_import_excel', 'xinghui2_report_download_template',
    'changfu_report_edit', 'changfu_report_history', 'changfu_report_import_excel', 'changfu_report_download_template',
    # QC报表导出函数
    'export_dongtai_report_excel', 'export_dongtai_yesterday_production', 'export_dongtai_today_production',
    'export_dayuan_report_excel', 'export_dayuan_yesterday_production', 'export_dayuan_today_production',
    'export_yuantong_report_excel', 'export_yuantong_yesterday_production', 'export_yuantong_today_production',
    'export_yuantong2_report_excel', 'export_yuantong2_yesterday_production', 'export_yuantong2_today_production',
    'export_xinghui_report_excel', 'export_xinghui_yesterday_production', 'export_xinghui_today_production',
    'export_changfu_report_excel', 'export_changfu_yesterday_production', 'export_changfu_today_production',
    'export_xinghui2_report_excel', 'export_xinghui2_yesterday_production', 'export_xinghui2_today_production',
    # 微信认证
    'WeChatUserListAPI',
    'WeChatCallbackView',
    'WeChatMessageReceiveView',
    'wechat_login',
    'custom_logout',
    # 其他视图（延迟导入）
    'PermissionAPI',
    'HomeView',
    'IndexView',
    'ParameterConfigView',
    'ProductionHistoryView',
    'PasswordLoginAPI',
    'RawSoilStorageView',
    'UserManagementAPI',
    'UserPasswordResetAPI',
    'RBACRoleAPI',
    'RBACPermissionAPI',
    'RBACUserRoleAPI',
    'RBACRolePermissionAPI',
    'rbac_management',
    'get_parameter',
    'InventoryOrgAPI',
    'MaterialMappingAPI',
    'WarehouseMappingAPI',
    'CostCenterMappingAPI',
    'CostObjectMappingAPI',
    'WaterDeductionRateAPI',
    'OperationObjectAPI',
    'ProductModelAPI',
    'PackagingAPI',
    'UserFavoriteAPI',
]
