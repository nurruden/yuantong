from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from datetime import date

class NullableFloatField(models.FloatField):
    """自定义FloatField，可以将空字符串转换为None"""
    
    def to_python(self, value):
        if value == '':
            return None
        return super().to_python(value)
    
    def get_prep_value(self, value):
        if value == '':
            return None
        return super().get_prep_value(value)

class InventoryOrg(models.Model):
    org_name = models.CharField(max_length=100)
    org_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_org'

class WaterDeductionRate(models.Model):
    inventory_org = models.ForeignKey(InventoryOrg, on_delete=models.CASCADE, related_name='water_deduction_rates')
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'water_deduction_rate'
        unique_together = ['inventory_org']

class MaterialMapping(models.Model):
    material_code = models.CharField(max_length=50, unique=True)
    material_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'material_mapping'
        
    def __str__(self):
        return f"{self.material_code} - {self.material_name}"

class WarehouseMapping(models.Model):
    warehouse_code = models.CharField(max_length=50, unique=True)
    warehouse_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warehouse_mapping'
        
    def __str__(self):
        return f"{self.warehouse_code} - {self.warehouse_name}"

class CostCenterMapping(models.Model):
    cost_center_code = models.CharField(max_length=50, unique=True)
    cost_center_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cost_center_mapping'
        
    def __str__(self):
        return f"{self.cost_center_code} - {self.cost_center_name}"

class CostObjectMapping(models.Model):
    cost_object_code = models.CharField(max_length=50, unique=True)
    cost_object_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cost_object_mapping'
        
    def __str__(self):
        return f"{self.cost_object_code} - {self.cost_object_name}"

class OperationObject(models.Model):
    user_id = models.CharField(max_length=50)
    inventory_org = models.ForeignKey(InventoryOrg, on_delete=models.CASCADE, related_name='operation_objects')
    warehouse = models.ForeignKey(WarehouseMapping, on_delete=models.CASCADE, related_name='operation_objects')
    cost_center = models.ForeignKey(CostCenterMapping, on_delete=models.CASCADE, related_name='operation_objects')
    cost_object = models.ForeignKey(CostObjectMapping, on_delete=models.CASCADE, related_name='operation_objects')
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'operation_object'
        unique_together = ['user_id', 'inventory_org', 'warehouse', 'cost_center', 'cost_object']
    
    def __str__(self):
        return f"{self.user_id} - {self.inventory_org.org_name} - {self.warehouse.warehouse_name}"


class RawSoilStorage(models.Model):
    """原土入库本地记录，与EAS同步"""
    fnumber = models.CharField('单据编号', max_length=100, unique=True, db_index=True)
    biz_date = models.DateField('业务日期')
    material_code = models.CharField('物料编码', max_length=50)
    material_name = models.CharField('物料名称', max_length=100)
    quantity = models.DecimalField('入库数量', max_digits=18, decimal_places=4, default=0)
    actual_quantity = models.DecimalField('真实入库数量', max_digits=18, decimal_places=4, default=0,
                                          help_text='入库数量*(1-扣水率)')
    lot = models.CharField('批次号', max_length=100, blank=True, default='')
    remark = models.TextField('备注', blank=True, default='')
    cost_center_code = models.CharField('成本中心编码', max_length=50)
    storage_org_code = models.CharField('库存组织编码', max_length=50)
    warehouse_code = models.CharField('仓库编码', max_length=50)
    cost_object_code = models.CharField('成本对象编码', max_length=50)
    rate = models.DecimalField('扣水率', max_digits=5, decimal_places=2, default=0)
    created_by = models.CharField('创建人', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'raw_soil_storage'
        ordering = ['-biz_date', '-created_at']
        verbose_name = '原土入库记录'
        verbose_name_plural = '原土入库记录'

    def __str__(self):
        return f"{self.fnumber} - {self.material_name} - {self.biz_date}"


class QCReport(models.Model):
    """QC报表基础模型"""
    date = models.DateField('检测日期')
    material_code = models.CharField('物料编码', max_length=50)
    material_name = models.CharField('物料名称', max_length=100)
    batch_number = models.CharField('批次号', max_length=50)
    test_item = models.CharField('检测项目', max_length=100)
    test_result = models.CharField('检测结果', max_length=200)
    tester = models.CharField('检测人', max_length=50)
    remark = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-date', '-created_at']

class DongtaiQCReport(models.Model):
    """东泰QC报表"""
    # 基本信息
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    material_type = models.CharField('物料类型', max_length=50, default='助熔煅烧品', choices=[
        ('助熔煅烧品', '助熔煅烧品'),
        ('煅烧品', '煅烧品'),
    ])
    # 新增的三个字段
    dongtai_permeability_coefficient = models.FloatField('东泰渗透率系数', null=True, blank=True)
    dongtai_sample_weight = models.FloatField('东泰样品重量', null=True, blank=True)
    dongtai_filter_area = models.FloatField('东泰过滤面积', null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    yuantong_cake_density = models.FloatField('远通饼密度(g/cm3)', null=True, blank=True)
    changfu_cake_density = models.FloatField('长富饼密度(g/cm3)', null=True, blank=True)
    filter_time = models.FloatField('过滤时间(秒)', null=True, blank=True)
    water_viscosity = models.DecimalField('水黏度(mPa.s)', max_digits=8, decimal_places=4, null=True, blank=True)
    cake_thickness = models.FloatField('饼厚(mm)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.CharField('涡值(cm)', max_length=100, null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=3, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_100m = models.CharField('+100M (%)', max_length=100, blank=True, null=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dongtai_reports',
                             verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除 也能保留记录


    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '东泰QC报表'
        verbose_name_plural = '东泰QC报表'
        # db_table = 'dongtai_qc_report'

    def __str__(self):
        return f"{self.date} - {self.product_name}"

class ChangfuQCReport(models.Model):
    """长富QC报表"""
    # 基本信息
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    filter_time = models.FloatField('过滤时间(秒)', null=True, blank=True)
    water_viscosity = models.DecimalField('水黏度(mPa.s)', max_digits=8, decimal_places=4, null=True, blank=True)
    cake_thickness = models.FloatField('饼厚(mm)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.FloatField('涡值(cm)', null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=4, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_100m = models.CharField('+100M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='changfu_reports',
                             verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除 也能保留记录


    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '长富QC报表'
        verbose_name_plural = '长富QC报表'
        # db_table = 'changfu_qc_report'

    def __str__(self):
        return f"{self.date} - {self.product_name}"

class DayuanQCReport(models.Model):
    """大塬QC报表"""
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.FloatField('涡值(cm)', null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=3, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_100m = models.CharField('+100M (%)', max_length=100, blank=True, null=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dayuan_reports', verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除也能保留记录

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '大塬QC报表'
        verbose_name_plural = '大塬QC报表'

    def __str__(self):
        return f"{self.date} - {self.product_name}"

class XinghuiQCReport(models.Model):
    """兴辉QC报表"""
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    xinghui_permeability = models.FloatField('兴辉渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    filter_time = models.FloatField('过滤时间(秒)', null=True, blank=True)
    water_viscosity = models.DecimalField('水黏度(mPa.s)', max_digits=8, decimal_places=4, null=True, blank=True)
    cake_thickness = models.FloatField('饼厚(mm)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.FloatField('涡值(cm)', null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=3, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_100m = models.CharField('+100M (%)', max_length=100, blank=True, null=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='xinghui_reports', verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除也能保留记录

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '兴辉QC报表'
        verbose_name_plural = '兴辉QC报表'

    def __str__(self):
        return f"{self.date} - {self.product_name}"

class Xinghui2QCReport(models.Model):
    """兴辉QC报表"""
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    xinghui_permeability = models.FloatField('兴辉渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    filter_time = models.FloatField('过滤时间(秒)', null=True, blank=True)
    water_viscosity = models.DecimalField('水黏度(mPa.s)', max_digits=8, decimal_places=4, null=True, blank=True)
    cake_thickness = models.FloatField('饼厚(mm)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.FloatField('涡值(cm)', null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=3, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_100m = models.CharField('+100M (%)', max_length=100, blank=True, null=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='xinghui2_reports', verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除也能保留记录

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '兴辉二线QC报表'
        verbose_name_plural = '兴辉二线QC报表'

    def __str__(self):
        return f"{self.date} - {self.product_name}"


class YuantongQCReport(models.Model):
    """远通QC报表"""
    # 基本信息
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    material_type = models.CharField('物料类型', max_length=50, default='助熔煅烧品', choices=[
        ('助熔煅烧品', '助熔煅烧品'),
        ('煅烧品', '煅烧品'),
    ])
    # 新增的三个字段
    yuantong_permeability_coefficient = models.FloatField('远通渗透率系数', null=True, blank=True)
    yuantong_sample_weight = models.FloatField('远通样品重量', null=True, blank=True)
    yuantong_filter_area = models.FloatField('远通过滤面积', null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    yuantong_cake_density = models.FloatField('远通饼密度(g/cm3)', null=True, blank=True)
    changfu_cake_density = models.FloatField('长富饼密度(g/cm3)', null=True, blank=True)
    filter_time = models.FloatField('过滤时间(秒)', null=True, blank=True)
    water_viscosity = models.DecimalField('水黏度(mPa.s)', max_digits=8, decimal_places=4, null=True, blank=True)
    cake_thickness = models.FloatField('饼厚(mm)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.FloatField('涡值(cm)', null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=3, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_100m = models.CharField("+100M (%)", max_length=100, blank=True, null=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='yuantong_reports',
                             verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除 也能保留记录


    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '远通QC报表'
        verbose_name_plural = '远通QC报表'
        # db_table = 'yuantong_qc_report'

    def __str__(self):
        return f"{self.date} - {self.product_name}"

class Yuantong2QCReport(models.Model):
    """远通2QC报表"""
    # 基本信息
    date = models.DateField('日期', default=date.today)
    time = models.TimeField('时间', default='00:00')
    shift = models.CharField('班次', max_length=10, default='')
    product_name = models.CharField('产品名称', max_length=100, default='')
    packaging = models.CharField('包装类型', max_length=50, default='')
    batch_number = models.CharField('批号', max_length=50, default='')
    moisture_after_drying = models.FloatField('干燥后原土水分(%)', null=True, blank=True)
    alkali_content = models.FloatField('入窑前碱含量(%)', null=True, blank=True)
    flux = models.CharField('助溶剂添加比例', max_length=50, null=True, blank=True)
    material_type = models.CharField('物料类型', max_length=50, default='助熔煅烧品', choices=[
        ('助熔煅烧品', '助熔煅烧品'),
        ('煅烧品', '煅烧品'),
    ])
    # 新增的三个字段
    yuantong_permeability_coefficient = models.FloatField('远通渗透率系数', null=True, blank=True)
    yuantong_sample_weight = models.FloatField('远通样品重量', null=True, blank=True)
    yuantong_filter_area = models.FloatField('远通过滤面积', null=True, blank=True)
    permeability = models.FloatField('远通渗透率(Darcy)', null=True, blank=True)
    permeability_long = models.FloatField('长富渗透率(Darcy)', null=True, blank=True)
    wet_cake_density = models.FloatField('饼密度(g/cm3)', null=True, blank=True)
    yuantong_cake_density = models.FloatField('远通饼密度(g/cm3)', null=True, blank=True)
    changfu_cake_density = models.FloatField('长富饼密度(g/cm3)', null=True, blank=True)
    filter_time = models.FloatField('过滤时间(秒)', null=True, blank=True)
    water_viscosity = models.DecimalField('水黏度(mPa.s)', max_digits=8, decimal_places=4, null=True, blank=True)
    cake_thickness = models.FloatField('饼厚(mm)', null=True, blank=True)
    bulk_density = models.FloatField('振实密度(g/cm3)', null=True, blank=True)
    brightness = models.FloatField('白度', null=True, blank=True)
    swirl = models.FloatField('涡值(cm)', null=True, blank=True)
    odor = NullableFloatField('气味', null=True, blank=True)
    conductance = models.FloatField('电导值(ms/cm)', null=True, blank=True)
    ph = models.FloatField('pH', null=True, blank=True)
    moisture = models.FloatField('水分(%)', null=True, blank=True)
    bags = models.FloatField('袋数', null=True, blank=True)
    tons = models.DecimalField('吨', max_digits=10, decimal_places=3, null=True, blank=True)
    sieving_14m = models.FloatField('+14M (%)', null=True, blank=True)
    sieving_30m = models.FloatField('+30M (%)', null=True, blank=True)
    sieving_40m = models.FloatField('+40M (%)', null=True, blank=True)
    sieving_80m = models.FloatField('+80M (%)', null=True, blank=True)
    sieving_100m = models.CharField("+100M (%)", max_length=100, blank=True, null=True)
    sieving_150m = models.CharField('+150M (%)', max_length=100, blank=True, null=True)
    sieving_200m = models.CharField('+200M (%)', max_length=100, blank=True, null=True)
    sieving_325m = models.CharField('+325M (%)', max_length=100, blank=True, null=True)
    fe_ion = models.FloatField('Fe离子', null=True, blank=True)
    ca_ion = models.FloatField('Ca离子', null=True, blank=True)
    al_ion = models.FloatField('Al离子', null=True, blank=True)
    oil_absorption = models.FloatField('吸油量', null=True, blank=True)
    water_absorption = models.FloatField('吸水量', null=True, blank=True)
    remarks = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    # 添加用户字段
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='yuantong2_reports',
                             verbose_name='用户')
    username = models.CharField('用户名', max_length=150, null=True)  # 存储用户名，即使用户被删除 也能保留记录


    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '远通QC报表'
        verbose_name_plural = '远通QC报表'
        # db_table = 'yuantong_qc_report'

    def __str__(self):
        return f"{self.date} - {self.product_name}"


class ProductModel(models.Model):
    """产品型号模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='产品型号名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '产品型号'
        verbose_name_plural = '产品型号'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Packaging(models.Model):
    """包装物模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='包装物名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '包装物'
        verbose_name_plural = '包装物'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class UserFavorite(models.Model):
    """用户收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    favorite_type = models.CharField('收藏类型', max_length=50, help_text='收藏的类型，如page、product等', default='page')
    favorite_id = models.CharField('收藏ID', max_length=100, help_text='收藏项目的ID', default='')
    favorite_name = models.CharField('收藏名称', max_length=200, help_text='收藏项目的显示名称', default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'
        unique_together = ('user', 'favorite_type', 'favorite_id')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.favorite_name}"

class Parameter(models.Model):
    """系统参数模型"""
    id = models.CharField(max_length=50, primary_key=True, verbose_name='参数ID')
    name = models.CharField(max_length=100, verbose_name='参数名称')
    value = models.CharField(max_length=500, verbose_name='参数值')
    description = models.TextField(blank=True, null=True, verbose_name='参数描述')
    group = models.CharField(max_length=100, verbose_name='参数分组', default='默认分组')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '系统参数'
        verbose_name_plural = '系统参数'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.id})"

class UserProfile(models.Model):
    """用户扩展信息模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField('电话', max_length=20, blank=True, null=True)
    wechat_id = models.CharField('企业微信ID', max_length=100, blank=True, null=True)
    encrypted_password = models.CharField('加密密码', max_length=255, blank=True, null=True, help_text='用于用户名密码登录验证的加密密码')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'
        db_table = 'user_profile'

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name or self.user.username}"


class MenuPermission(models.Model):
    """菜单权限模型"""
    menu_name = models.CharField('菜单名称', max_length=100, help_text='菜单的名称，如"系统设置"')
    allowed_users = models.TextField('允许访问的用户', blank=True, null=True, help_text='允许访问此菜单的用户ID列表，用逗号分隔')
    is_active = models.BooleanField('是否生效', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)


    class Meta:
        verbose_name = '菜单权限'
        verbose_name_plural = '菜单权限'
        db_table = 'menu_permission'
        unique_together = ('menu_name', 'is_active')

    def __str__(self):
        return f"{self.menu_name} - {self.allowed_users}"
    
    def get_allowed_users_list(self):
        """获取允许访问的用户列表"""
        if not self.allowed_users:
            return []
        return [user.strip() for user in self.allowed_users.split(',') if user.strip()]

class UserOperationLog(models.Model):
    """用户操作日志模型"""
    OPERATION_TYPES = [
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除'),
        ('VIEW', '查看'),
        ('EXPORT', '导出'),
        ('LOGIN', '登录'),
        ('LOGOUT', '登出'),
    ]
    
    REPORT_TYPES = [
        ('dongtai', '东泰QC报表'),
        ('yuantong', '远通QC报表'),
        ('yuantong2', '远通2号QC报表'),
        ('dayuan', '大塬QC报表'),
        ('changfu', '长富QC报表'),
        ('xinghui', '兴辉QC报表'),
        ('xinghui2', '兴辉2号QC报表'),
    ]
    
    # 基本信息
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='operation_logs', verbose_name='操作用户')
    username = models.CharField('用户名', max_length=150)
    
    # 操作信息
    operation_type = models.CharField('操作类型', max_length=20, choices=OPERATION_TYPES)
    report_type = models.CharField('报表类型', max_length=20, choices=REPORT_TYPES, null=True, blank=True)
    report_id = models.IntegerField('报表ID', null=True, blank=True)
    
    # 操作详情
    operation_detail = models.TextField('操作详情', blank=True)
    old_data = models.JSONField('旧数据', null=True, blank=True)
    new_data = models.JSONField('新数据', null=True, blank=True)
    
    # 请求信息
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    request_path = models.CharField('请求路径', max_length=500)
    request_method = models.CharField('请求方法', max_length=10)
    
    # 时间信息
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'user_operation_log'
        ordering = ['-created_at']
        verbose_name = '用户操作日志'
        verbose_name_plural = '用户操作日志'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['operation_type', 'created_at']),
            models.Index(fields=['report_type', 'created_at']),
            models.Index(fields=['username', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.get_operation_type_display()} - {self.get_report_type_display() if self.report_type else '系统操作'} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @classmethod
    def log_operation(cls, request, operation_type, report_type=None, report_id=None, 
                     operation_detail='', old_data=None, new_data=None):
        """记录用户操作的便捷方法"""
        try:
            from decimal import Decimal
            import datetime
            
            user = request.user if hasattr(request, 'user') else None
            username = user.username if user and user.is_authenticated else 'anonymous'
            
            # 获取客户端IP地址
            ip_address = cls._get_client_ip(request)
            
            # 获取用户代理
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500] if hasattr(request, 'META') else ''
            
            # 获取请求路径和方法
            request_path = request.path if hasattr(request, 'path') else ''
            request_method = request.method if hasattr(request, 'method') else ''
            
            # 处理old_data和new_data，确保可以JSON序列化
            def serialize_for_json(data):
                """将数据转换为可JSON序列化的格式"""
                if data is None:
                    return None
                if isinstance(data, dict):
                    return {k: serialize_for_json(v) for k, v in data.items()}
                elif isinstance(data, (list, tuple)):
                    return [serialize_for_json(item) for item in data]
                elif isinstance(data, Decimal):
                    # Decimal类型转换为float
                    return float(data)
                elif isinstance(data, (datetime.date, datetime.datetime)):
                    # 日期时间对象转换为字符串
                    return data.isoformat()
                elif hasattr(data, '__dict__'):
                    # 复杂对象转换为字符串
                    return str(data)
                else:
                    return data
            
            # 序列化old_data和new_data
            serialized_old_data = serialize_for_json(old_data) if old_data is not None else None
            serialized_new_data = serialize_for_json(new_data) if new_data is not None else None
            
            # 创建日志记录
            log_entry = cls.objects.create(
                user=user,
                username=username,
                operation_type=operation_type,
                report_type=report_type,
                report_id=report_id,
                operation_detail=operation_detail,
                old_data=serialized_old_data,
                new_data=serialized_new_data,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
                request_method=request_method,
            )
            
            # 同时记录到Django日志
            import logging
            logger = logging.getLogger('user_operations')
            logger.info(f"用户操作日志: {log_entry}")
            
            return log_entry
            
        except Exception as e:
            # 如果日志记录失败，记录到Django日志
            import logging
            logger = logging.getLogger('user_operations')
            logger.error(f"记录用户操作日志失败: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def _get_client_ip(request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip