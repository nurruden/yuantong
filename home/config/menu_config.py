"""
菜单配置模块
提供系统菜单结构和微信配置
"""

from django.conf import settings


# 共享的菜单数据
MENU_ITEMS = [
    {
        'name': '业务管理',
        'icon': 'storefront',
        'children': [
            {'name': '销售订单', 'icon': 'receipt_long'},
            {'name': '采购订单', 'icon': 'shopping_cart'},
            {'name': '合同管理', 'icon': 'description'},
        ]
    },
    {
        'name': '生产管理',
        'icon': 'factory',
        'children': [
            {'name': '原土入库', 'icon': 'inventory', 'url': '/production/raw-soil-storage/'},
            {'name': 'QC报表', 'icon': 'fact_check', 'url': '/qc_report/'},
            {'name': '设备维护', 'icon': 'build'},
        ]
    },
    {
        'name': '仓储物流',
        'icon': 'inventory_2',
        'children': [
            {'name': '入库管理', 'icon': 'input'},
            {'name': '出库管理', 'icon': 'output'},
            {'name': '库存查询', 'icon': 'search'},
        ]
    },
    {
        'name': '财务管理',
        'icon': 'account_balance',
        'children': [
            {'name': '应收账款', 'icon': 'payments'},
            {'name': '应付账款', 'icon': 'credit_score'},
            {'name': '财务报表', 'icon': 'analytics'},
        ]
    },
    {
        'name': '人力资源',
        'icon': 'diversity_3',
        'children': [
            {'name': '员工信息', 'icon': 'person'},
            {'name': '考勤管理', 'icon': 'event_available'},
            {'name': '绩效考核', 'icon': 'assessment'},
        ]
    },
    {
        'name': '系统设置',
        'icon': 'settings',
        'children': [
            {'name': '参数配置', 'icon': 'tune'},
            {'name': '用户管理', 'icon': 'people'},
            {'name': '用户权限管理', 'icon': 'admin_panel_settings'},
            {'name': '权限管理', 'icon': 'lock'},
            {'name': '产品型号', 'icon': 'category'},
            {'name': '包装物管理', 'icon': 'inventory'},
            {'name': '任务管理', 'icon': 'schedule'},
            {"name": "操作日志", "icon": "history"},
        ]
    }
]


def get_wechat_config():
    """
    获取企业微信配置
    
    Returns:
        dict: 包含corp_id, secret, agent_id的配置字典
    """
    return {
        'corp_id': settings.WECHAT_CORP_ID,
        'secret': settings.WECHAT_CORP_SECRET,  # 使用 CORP_SECRET
        'agent_id': settings.WECHAT_AGENT_ID
    }
