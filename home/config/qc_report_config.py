"""
QC报表配置模块
提供QC报表相关的配置数据，包括字段映射、模块代码映射等
"""

# QC报表字段映射配置
QC_REPORT_FIELD_MAPPING = {
    'date': 'Date日期',
    'time': 'Time时间',
    'moisture_after_drying': 'Moisture after drying烘干后原土水分（%）',
    'alkali_content': 'Alkali content入窑前碱含量(%)',
    'flux': '*flux agent 助溶剂添加比例',
    'product_name': 'Grade 产品型号',
    'permeability': 'Permeability远通渗透率(Darcy)',
    'permeability_long': 'Permeability长富渗透率(Darcy)',
    'xinghui_permeability': 'Permeability兴辉渗透率(Darcy)',
    'wet_cake_density': 'Wet cake density饼密度(g/cm3)',
    'yuantong_cake_density': '远通饼密度(g/cm3)',
    'changfu_cake_density': '长富饼密度(g/cm3)',
    'filter_time': '过滤时间(秒)',
    'water_viscosity': '水黏度(mPa.s)',
    'cake_thickness': '饼厚(mm)',
    'bulk_density': 'Tap density振实密度（g/cm3)',
    'sieving_14m': '+14M',
    'sieving_30m': '+30M',
    'sieving_40m': '+40M',
    'sieving_80m': '+80M',
    'sieving_100m': '+100M',
    'sieving_150m': '+150M',
    'sieving_200m': '+200M',
    'sieving_325m': '+325M',
    'fe_ion': 'Fe铁离子(mg/kg)',
    'ca_ion': 'Ca钙离子(mg/kg)',
    'al_ion': 'Al铝离子(mg/kg)',
    'brightness': 'Bri.白度',
    'swirl': 'Swirl涡值(cm)',
    'odor': 'Odor气味',
    'conductance': 'Conductance电导值(ms/cm)',
    'ph': 'pH',
    'oil_absorption': 'Oil absorption吸油率（%）',
    'water_absorption': 'Water absorption吸水率（%）',
    'moisture': 'Moisture水分   （%）',
    'bags': 'Bags袋数',
    'packaging': 'IPKP CODE包装类型',
    'tons': 'Tons吨',
    'batch_number': 'LOT批号/日期',
    'remarks': 'Notes备注',
    'shift': 'Squad 班组',
    'username': '操作人'
}


# QC报表模块名称到权限代码的映射
QC_REPORT_MODULE_TO_CODE = {
    '远通QC报表': 'yuantong_qc_report',
    '大塬QC报表': 'dayuan_qc_report',
    '东泰QC报表': 'dongtai_qc_report',
    '兴辉QC报表': 'xinghui_qc_report',
    '长富QC报表': 'changfu_qc_report',
    '远通二线QC报表': 'yuantong2_qc_report',
    '兴辉二线QC报表': 'xinghui2_qc_report',
    # 添加简化的模块名称映射
    '远通': 'yuantong_qc_report',
    '大塬': 'dayuan_qc_report',
    '东泰': 'dongtai_qc_report',
    '兴辉': 'xinghui_qc_report',
    '长富': 'changfu_qc_report',
    '远通二线': 'yuantong2_qc_report',
    '兴辉二线': 'xinghui2_qc_report',
}


# QC报表模块名称到权限代码的映射（用于权限检查）
QC_REPORT_MODULE_TO_PERMISSION = {
    '大塬QC报表': 'dayuan_qc_report',
    '东泰QC报表': 'dongtai_qc_report',
    '远通QC报表': 'yuantong_qc_report',
    '远通二线QC报表': 'yuantong2_qc_report',
    '兴辉QC报表': 'xinghui_qc_report',
    '兴辉二线QC报表': 'xinghui2_qc_report',
    '长富QC报表': 'changfu_qc_report',
    # 添加简化的模块名称映射
    '大塬': 'dayuan_qc_report',
    '东泰': 'dongtai_qc_report',
    '远通': 'yuantong_qc_report',
    '远通二线': 'yuantong2_qc_report',
    '兴辉': 'xinghui_qc_report',
    '兴辉二线': 'xinghui2_qc_report',
    '长富': 'changfu_qc_report',
}


def get_report_module_code(module_name):
    """
    根据模块名称获取对应的权限代码
    
    Args:
        module_name: 模块名称（如'远通QC报表'、'大塬'等）
    
    Returns:
        str: 权限代码（如'yuantong_qc_report'）
    """
    return QC_REPORT_MODULE_TO_CODE.get(
        module_name, 
        module_name.lower().replace(' ', '_')
    )


def get_report_permission_code(module_name):
    """
    根据模块名称获取对应的权限代码（用于权限检查）
    
    Args:
        module_name: 模块名称（如'远通QC报表'、'大塬'等）
    
    Returns:
        str: 权限代码（如'yuantong_qc_report'）
    """
    return QC_REPORT_MODULE_TO_PERMISSION.get(
        module_name,
        module_name.lower().replace(' ', '_')
    )
