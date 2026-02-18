from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_GET
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import os
import json
from wechatpy.enterprise.client import WeChatClient
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from openpyxl import Workbook
import logging
import urllib.parse
import hashlib
import requests
from functools import wraps

# 导入配置
from home.config import (
    MENU_ITEMS,
    QC_REPORT_FIELD_MAPPING,
    get_wechat_config,
    get_report_module_code,
    get_report_permission_code,
)

# 导入工具函数
from home.utils.excel_export import (
    export_production_excel,
    export_qc_report_excel,
    export_qc_report_excel_universal,
)
from home.utils.permissions import (
    user_has_permission,
    permission_required,
    system_settings_required,
    has_system_settings_permission,
    filter_menu_by_permission,
)
from home.utils.user_helpers import (
    get_user_info,
    is_admin_user,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from .models import (
    InventoryOrg, MaterialMapping, WarehouseMapping, CostCenterMapping,
    CostObjectMapping, WaterDeductionRate, OperationObject, DongtaiQCReport,
    DayuanQCReport, XinghuiQCReport, ChangfuQCReport, YuantongQCReport, Yuantong2QCReport, Packaging, ProductModel, UserFavorite, Parameter, UserProfile,Xinghui2QCReport
)
from system.models import Department, Position, UserProfile as SystemUserProfile
from system.models import Permission,Company


# ==================== QC报表通用基类和工具函数 ====================

# ==================== QC报表通用基类和工具函数 ====================



# export_production_excel 已移动到 home.utils.excel_export
# export_qc_report_excel 已移动到 home.utils.excel_export  
# export_qc_report_excel_universal 已移动到 home.utils.excel_export
# get_user_info 已移动到 home.utils.user_helpers
# is_admin_user 已移动到 home.utils.user_helpers
# has_system_settings_permission 已移动到 home.utils.permissions
# filter_menu_by_permission 已移动到 home.utils.permissions
# system_settings_required 已移动到 home.utils.permissions

# 以上函数已移动到 home.utils.excel_export
# get_user_info 已移动到 home.utils.user_helpers
# system_settings_required 已移动到 home.utils.permissions


# 权限设置页面视图
# 菜单结构定义（如需调整请在此处修改）

# 权限API
class PermissionAPI(View):
    def get(self, request):
        """获取权限配置"""
        from home.models import MenuPermission
        
        try:
            permissions = []
            permission_objects = MenuPermission.objects.filter(is_active=True)
            
            for perm in permission_objects:
                permissions.append({
                    "page": perm.menu_name,
                    "users": perm.allowed_users.split(',') if perm.allowed_users else []
                })
            
            # 如果没有系统设置权限配置，添加默认配置
            system_permission_exists = any(p['page'] == '系统设置' for p in permissions)
            if not system_permission_exists:
                permissions.append({
                    "page": "系统设置",
                    "users": ["GaoBieKeLe", "yanyanzhao"]
                })
            
            return JsonResponse({"permissions": permissions})
        except Exception as e:
            # 获取权限配置出错: e
            # 返回默认配置
            return JsonResponse({
                "permissions": [
                    {"page": "系统设置", "users": ["GaoBieKeLe", "yanyanzhao"]}
                ]
            })

    def post(self, request):
        """保存权限配置"""
        from home.models import MenuPermission
        
        try:
            config = json.loads(request.body)
            permissions = config.get('permissions', [])
            
            # 清空现有权限配置
            MenuPermission.objects.filter(is_active=True).update(is_active=False)
            
            # 保存新的权限配置
            for perm in permissions:
                menu_name = perm.get('page', '')
                users = perm.get('users', [])
                users_str = ','.join(users) if users else ''
                
                if menu_name:
                    MenuPermission.objects.update_or_create(
                        menu_name=menu_name,
                        defaults={
                            'allowed_users': users_str,
                            'is_active': True
                        }
                    )
            
            return JsonResponse({'success': True, 'message': '权限配置保存成功'})
        except Exception as e:
            # 保存权限配置出错: e
            return JsonResponse({'success': False, 'error': f'保存失败: {str(e)}'})


# 企业微信用户列表API
# 微信认证相关代码已移动到 home/views/wechat_auth.py
@method_decorator(login_required, name='dispatch')
class ProductionHistoryView(View):
    def get(self, request):
        # 检查用户是否有生产历史查看权限
        if not user_has_permission(request.user, 'production_history_view'):
            # 渲染美观的403错误页面
            context = {
                'user': request.user,
                'request_path': request.path,
                'permission_code': 'production_history_view'
            }
            return render(request, '403.html', context, status=403)
        
        import requests

        logger = logging.getLogger(__name__)
        logger.info("进入 ProductionHistoryView.get 方法")

        context = {}
        user_id = request.user.username
        logger.info(f"当前用户 user_id: {user_id}")
        
        # 检查是否为特殊用户（GaoBieKeLe或JinShui）
        special_users = ['GaoBieKeLe', 'JinShui']
        is_special_user = user_id in special_users
        logger.info(f"是否为特殊用户: {is_special_user}")
        
        # 计算默认日期范围
        today = date.today()
        prev_month = today + relativedelta(months=-1)
        try:
            date_prev = prev_month.replace(day=29)
        except ValueError:
            # 如果上个月没有29号，则返回本月1号
            date_prev = today.replace(day=1)
        next_month_1st = today + relativedelta(months=+1, day=1)
        
        # 默认的API查询日期范围
        biz_date_start = date_prev.strftime("%Y-%m-%d")
        biz_date_end = next_month_1st.strftime("%Y-%m-%d")
        logger.info(f"默认API查询日期范围: {biz_date_start} ~ {biz_date_end}")

        # 分页参数
        page_size = int(request.GET.get('page_size', 10))  # 每页显示数量
        page = int(request.GET.get('page', 1))  # 当前页码
        logger.info(f"分页参数 page_size: {page_size}, page: {page}")
        
        # 搜索参数
        warehouse_filter = request.GET.get('warehouse', '')
        start_date_filter = request.GET.get('start_date', '')
        end_date_filter = request.GET.get('end_date', '')
        
        # 处理搜索日期范围，确保不超过默认范围
        effective_start_date = date_prev
        effective_end_date = next_month_1st
        
        if start_date_filter:
            try:
                user_start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
                # 如果用户输入的起始日期晚于默认起始日期，使用用户输入的日期
                if user_start_date > date_prev:
                    effective_start_date = user_start_date
            except ValueError:
                logger.warning(f"无效的起始日期格式: {start_date_filter}")
        
        if end_date_filter:
            try:
                user_end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()
                # 如果用户输入的结束日期早于默认结束日期，使用用户输入的日期
                if user_end_date < next_month_1st:
                    effective_end_date = user_end_date
            except ValueError:
                logger.warning(f"无效的结束日期格式: {end_date_filter}")
        
        logger.info(f"有效搜索日期范围: {effective_start_date} ~ {effective_end_date}")
        logger.info(f"搜索参数 warehouse: {warehouse_filter}, start_date: {start_date_filter}, end_date: {end_date_filter}")

        if is_special_user:
            # 特殊用户：获取所有库存组织和仓库组合
            try:
                operation_objects = OperationObject.objects.select_related(
                    'inventory_org', 'warehouse'
                ).all()
                logger.info(f"特殊用户查询所有操作对象，共{operation_objects.count()}个")
                
                all_records = []
                total_orgs = operation_objects.count()
                
                # 特殊用户：获取所有数据，不传递分页参数给外部API
                for operation_object in operation_objects:
                    org_code = operation_object.inventory_org.org_code
                    warehouse_code = operation_object.warehouse.warehouse_code
                    logger.info(f"查询组织: {org_code}, 仓库: {warehouse_code}")
                    
                    # 构造POST数据 - 不传递分页参数，获取所有数据
                    post_data = {
                        "orgNumber": org_code,
                        "WarehouseNumber": warehouse_code,
                        "pageNum": 1000,  # 设置一个很大的数，获取所有数据
                        "page": 1,  # 固定为第1页
                        "bizDateStart": biz_date_start,
                        "bizDateEnd": biz_date_end
                    }
                    api_url = settings.EAS_API_HOST + settings.EAS_API_PATH_GET
                    logger.info(f"POST到外部API: {api_url}, 数据: {post_data}")

                    try:
                        resp = requests.post(api_url, json=post_data, timeout=10)
                        logger.info(f"外部API响应状态码: {resp.status_code}")
                        resp.raise_for_status()
                        data = resp.json()
                        logger.info(f"API返回数据: {data}")
                        
                        # 兼容不同API返回结构
                        records = data.get('data') or data.get('sysnList') or []
                        
                        # 转换字段用于模板渲染，兼容多种字段名
                        # 渲染每条记录下的 entry 明细
                        for rec in records:
                            FBizDate = rec.get('FBizDate')
                            storageOrgUnitName = rec.get('storageOrgUnitName')
                            entry_list = rec.get('entry') or []
                            for entry in entry_list:
                                warehouse_name = entry.get('WarehouseName')
                                material_name = entry.get('materialName')
                                quantity = entry.get('FQty')
                                cost_center = rec.get('costCenterOrgUnitName')
                                batch_number = entry.get('FLot')
                                material_number = entry.get('materialNumber')
                                FNumber = rec.get('FNumber')
                                logger.debug(
                                    f"entry调试: WarehouseName={warehouse_name}, materialName={material_name}, FQty={quantity}, costCenterOrgUnitName={cost_center}, FLot={batch_number}, materialNumber={material_number}")
                                all_records.append({
                                    'warehouse_name': warehouse_name,
                                    'FBizDate': FBizDate,
                                    'storageOrgUnitName': storageOrgUnitName,
                                    'material_name': material_name,
                                    'quantity': quantity,
                                    'cost_center': cost_center,
                                    'batch_number': batch_number,
                                    'materialNumber': material_number,
                                    'FNumber': FNumber,
                                    'org_code': org_code,  # 添加组织编码
                                    'warehouse_code': warehouse_code,  # 添加仓库编码
                                })
                    except Exception as e:
                        logger.error(f"特殊用户查询组织 {org_code} 仓库 {warehouse_code} 失败: {str(e)}", exc_info=True)
                        # 继续查询其他组织，不中断整个流程
                        continue
                
                # 应用搜索过滤
                filtered_records = []
                for record in all_records:
                    # 仓库过滤
                    if warehouse_filter and record.get('warehouse_code') != warehouse_filter:
                        continue
                    
                    # 日期过滤 - 使用有效日期范围
                    record_date = record.get('FBizDate', '')
                    if record_date:
                        try:
                            record_date_obj = datetime.strptime(record_date[:10], '%Y-%m-%d').date()
                            
                            # 检查记录日期是否在有效范围内
                            if record_date_obj < effective_start_date or record_date_obj > effective_end_date:
                                continue
                        except ValueError:
                            # 日期格式错误，跳过过滤
                            pass
                    
                    filtered_records.append(record)
                
                # 计算物料总重量
                material_total_weight = {}
                for record in filtered_records:
                    material_name = record.get('material_name', '')
                    quantity = record.get('quantity', 0)
                    
                    if material_name and quantity:
                        try:
                            quantity_float = float(quantity)
                            if material_name in material_total_weight:
                                material_total_weight[material_name] += quantity_float
                            else:
                                material_total_weight[material_name] = quantity_float
                        except (ValueError, TypeError):
                            # 数量格式错误，跳过
                            pass
                
                # 计算分页信息
                total_records = len(filtered_records)
                total_pages = (total_records + page_size - 1) // page_size
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                
                # 分页切片
                paginated_records = filtered_records[start_index:end_index]
                
                # 构建分页信息
                pagination = {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_records': total_records,
                    'page_size': page_size,
                    'has_previous': page > 1,
                    'has_next': page < total_pages,
                    'previous_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < total_pages else None,
                    'page_range': range(1, total_pages + 1)
                }
                
                context['records'] = paginated_records
                context['pagination'] = pagination
                
                # 添加搜索相关上下文
                context['warehouses'] = WarehouseMapping.objects.all()
                context['selected_warehouse'] = warehouse_filter
                context['start_date'] = start_date_filter
                context['end_date'] = end_date_filter
                
                # 添加默认日期范围
                context['default_start_date'] = date_prev.strftime("%Y-%m-%d")
                context['default_end_date'] = next_month_1st.strftime("%Y-%m-%d")
                
                # 添加物料总重量信息
                context['material_total_weight'] = material_total_weight
                
                logger.info(f"特殊用户最终记录列表: {len(paginated_records)}条记录，总记录: {total_records}，总页数: {total_pages}")
            except Exception as e:
                logger.error(f"历史记录POST请求失败: {str(e)}", exc_info=True)
                context['records'] = []
                context['error'] = f'历史记录获取失败: {str(e)}'
                context['pagination'] = None
                
                # 添加搜索相关上下文
                context['warehouses'] = WarehouseMapping.objects.all()
                context['selected_warehouse'] = warehouse_filter
                context['start_date'] = start_date_filter
                context['end_date'] = end_date_filter
                
                # 添加默认日期范围
                context['default_start_date'] = date_prev.strftime("%Y-%m-%d")
                context['default_end_date'] = next_month_1st.strftime("%Y-%m-%d")
                
                # 添加物料总重量信息（空字典）
                context['material_total_weight'] = {}
            
            # 添加菜单数据（函数和常量都在本文件中定义）
            context['menu_items'] = filter_menu_by_permission(MENU_ITEMS, request.user.username)
            
            return render(request, 'production/history.html', context)
        else:
            # 普通用户：使用自己的操作对象配置查询
            try:
                # 获取用户的操作对象配置
                operation_object = OperationObject.objects.get(user_id=request.user.username)
                org_code = operation_object.inventory_org.org_code
                warehouse_code = operation_object.warehouse.warehouse_code
                logger.info(f"普通用户 {request.user.username} 查询组织: {org_code}, 仓库: {warehouse_code}")
                
                # 构造POST数据 - 获取所有数据，然后在本地进行过滤和分页
                post_data = {
                    "orgNumber": org_code,
                    "WarehouseNumber": warehouse_code,
                    "pageNum": 1000,  # 设置一个很大的数，获取所有数据
                    "page": 1,  # 固定为第1页，获取所有数据
                    "bizDateStart": biz_date_start,
                    "bizDateEnd": biz_date_end
                }
                api_url = settings.EAS_API_HOST + settings.EAS_API_PATH_GET
                logger.info(f"普通用户POST到外部API: {api_url}, 数据: {post_data}")
                
                resp = requests.post(api_url, json=post_data, timeout=10)
                logger.info(f"外部API响应状态码: {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"API返回数据: {data}")
                
                # 兼容不同API返回结构
                records = data.get('data') or data.get('sysnList') or []
                
                # 转换字段用于模板渲染
                all_records = []
                for rec in records:
                    FBizDate = rec.get('FBizDate')
                    storageOrgUnitName = rec.get('storageOrgUnitName')
                    entry_list = rec.get('entry') or []
                    for entry in entry_list:
                        warehouse_name = entry.get('WarehouseName')
                        material_name = entry.get('materialName')
                        quantity = entry.get('FQty')
                        cost_center = rec.get('costCenterOrgUnitName')
                        batch_number = entry.get('FLot')
                        material_number = entry.get('materialNumber')
                        FNumber = rec.get('FNumber')
                        all_records.append({
                            'warehouse_name': warehouse_name,
                            'FBizDate': FBizDate,
                            'storageOrgUnitName': storageOrgUnitName,
                            'material_name': material_name,
                            'quantity': quantity,
                            'cost_center': cost_center,
                            'batch_number': batch_number,
                            'materialNumber': material_number,
                            'FNumber': FNumber,
                            'org_code': org_code,
                            'warehouse_code': warehouse_code,
                        })
                
                # 应用搜索过滤
                filtered_records = []
                for record in all_records:
                    # 仓库过滤
                    if warehouse_filter and record.get('warehouse_code') != warehouse_filter:
                        continue
                    
                    # 日期过滤
                    record_date = record.get('FBizDate', '')
                    if record_date:
                        try:
                            record_date_obj = datetime.strptime(record_date[:10], '%Y-%m-%d').date()
                            if record_date_obj < effective_start_date or record_date_obj > effective_end_date:
                                continue
                        except ValueError:
                            pass
                    
                    filtered_records.append(record)
                
                # 计算物料总重量
                material_total_weight = {}
                for record in filtered_records:
                    material_name = record.get('material_name', '')
                    quantity = record.get('quantity', 0)
                    if material_name and quantity:
                        try:
                            quantity_float = float(quantity)
                            if material_name in material_total_weight:
                                material_total_weight[material_name] += quantity_float
                            else:
                                material_total_weight[material_name] = quantity_float
                        except (ValueError, TypeError):
                            pass
                
                # 计算分页信息
                total_records = len(filtered_records)
                total_pages = (total_records + page_size - 1) // page_size
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                
                # 分页切片
                paginated_records = filtered_records[start_index:end_index]
                
                # 构建分页信息
                pagination = {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_records': total_records,
                    'page_size': page_size,
                    'has_previous': page > 1,
                    'has_next': page < total_pages,
                    'previous_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < total_pages else None,
                    'page_range': range(1, total_pages + 1)
                }
                
                context['records'] = paginated_records
                context['pagination'] = pagination
                
                # 添加搜索相关上下文
                context['warehouses'] = WarehouseMapping.objects.all()
                context['selected_warehouse'] = warehouse_filter
                context['start_date'] = start_date_filter
                context['end_date'] = end_date_filter
                
                # 添加默认日期范围
                context['default_start_date'] = date_prev.strftime("%Y-%m-%d")
                context['default_end_date'] = next_month_1st.strftime("%Y-%m-%d")
                
                # 添加物料总重量信息
                context['material_total_weight'] = material_total_weight
                
                logger.info(f"普通用户最终记录列表: {len(paginated_records)}条记录，总记录: {total_records}，总页数: {total_pages}")
            except OperationObject.DoesNotExist:
                logger.error(f"普通用户 {request.user.username} 未配置操作对象")
                context['records'] = []
                context['error'] = '您尚未配置操作对象，请联系管理员'
                context['pagination'] = None
                context['warehouses'] = WarehouseMapping.objects.all()
                context['selected_warehouse'] = warehouse_filter
                context['start_date'] = start_date_filter
                context['end_date'] = end_date_filter
                context['default_start_date'] = date_prev.strftime("%Y-%m-%d")
                context['default_end_date'] = next_month_1st.strftime("%Y-%m-%d")
                context['material_total_weight'] = {}
            except Exception as e:
                logger.error(f"普通用户历史记录获取失败: {str(e)}", exc_info=True)
                context['records'] = []
                context['error'] = f'历史记录获取失败: {str(e)}'
                context['pagination'] = None
                context['warehouses'] = WarehouseMapping.objects.all()
                context['selected_warehouse'] = warehouse_filter
                context['start_date'] = start_date_filter
                context['end_date'] = end_date_filter
                context['default_start_date'] = date_prev.strftime("%Y-%m-%d")
                context['default_end_date'] = next_month_1st.strftime("%Y-%m-%d")
                context['material_total_weight'] = {}
            
            # 添加菜单数据（函数和常量都在本文件中定义）
            context['menu_items'] = filter_menu_by_permission(MENU_ITEMS, request.user.username)
            
            return render(request, 'production/history.html', context)


# 微信认证相关代码已移动到 home/views/wechat_auth.py
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class ParameterConfigView(View):
    """参数配置视图"""

    def get(self, request):
        """获取参数配置页面"""
        # 获取所有参数
        parameters = Parameter.objects.all().order_by('group', 'name')

        # 按组分类参数
        parameter_groups = {}
        for param in parameters:
            if param.group not in parameter_groups:
                parameter_groups[param.group] = []
            parameter_groups[param.group].append(param)

        return render(request, 'system/parameter_config.html', {
            'parameter_groups': parameter_groups,
            'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
        })

    def post(self, request):
        """保存参数配置"""
        try:
            data = json.loads(request.body)
            param_id = data.get('id')
            value = data.get('value')

            if not param_id or value is None:
                return JsonResponse({'status': 'error', 'message': '参数ID和值不能为空'}, status=400)

            # 参数验证和处理
            if param_id == 'report_edit_limit':
                try:
                    value = int(value)
                    if value < 1 or value > 365:
                        return JsonResponse({'status': 'error', 'message': '编辑期限必须在1-365天之间'}, status=400)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': '编辑期限必须是有效的数字'}, status=400)

            elif param_id in ['yuantong_permeability_coefficient', 'dongtai_permeability_coefficient']:
                try:
                    value = float(value)
                    if value < 0.1 or value > 100:
                        return JsonResponse({'status': 'error', 'message': '渗透率系数必须在0.1-100之间'}, status=400)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': '渗透率系数必须是有效的数字'}, status=400)
            
            elif param_id in ['yuantong_sample_weight', 'dongtai_sample_weight']:
                try:
                    value = float(value)
                    if value < 0.1 or value > 1000:
                        return JsonResponse({'status': 'error', 'message': '样品重量必须在0.1-1000之间'}, status=400)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': '样品重量必须是有效的数字'}, status=400)
            
            elif param_id in ['yuantong_filter_area', 'dongtai_filter_area']:
                try:
                    value = float(value)
                    if value < 0.1 or value > 1000:
                        return JsonResponse({'status': 'error', 'message': '过滤面积必须在0.1-1000之间'}, status=400)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': '过滤面积必须是有效的数字'}, status=400)
            


            # 获取或创建参数
            parameter, created = Parameter.objects.get_or_create(
                id=param_id,
                defaults={
                    'name': get_parameter_name(param_id),
                    'value': str(value),
                    'group': '渗透率系数' if 'permeability' in param_id or 'cake_density' in param_id else '报表参数'
                }
            )
            
            if not created:
                parameter.value = str(value)
            parameter.save()

            return JsonResponse({'status': 'success', 'message': '参数保存成功'})
        except Parameter.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '参数不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in DepartmentAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, dept_id):
        """更新部门"""
        try:
            from system.models import Department
            
            data = json.loads(request.body)
            department = Department.objects.get(id=dept_id)
            
            if 'name' in data:
                department.name = data['name']
            if 'code' in data:
                # 检查代码是否与其他部门冲突
                if Department.objects.filter(code=data['code']).exclude(id=dept_id).exists():
                    return JsonResponse({'status': 'error', 'message': '部门代码已存在'}, status=400)
                department.code = data['code']
            if 'parent_id' in data:
                if data['parent_id']:
                    try:
                        parent = Department.objects.get(id=data['parent_id'])
                        # 防止循环引用
                        if parent.id == dept_id:
                            return JsonResponse({'status': 'error', 'message': '不能将自己设为父部门'}, status=400)
                        department.parent = parent
                        department.level = parent.level + 1
                    except Department.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': '父部门不存在'}, status=400)
                else:
                    department.parent = None
                    department.level = 1
            if 'description' in data:
                department.description = data['description']
            if 'is_active' in data:
                department.is_active = data['is_active']
            
            department.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '部门更新成功',
                'data': {
                    'id': department.id,
                    'name': department.name,
                    'code': department.code,
                    'level': department.level,
                    'description': department.description
                }
            })
            
        except Department.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '部门不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in DepartmentAPI.put: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, dept_id):
        """删除部门"""
        try:
            from system.models import Department
            
            department = Department.objects.get(id=dept_id)
            
            # 检查是否有子部门
            if department.department_set.exists():
                return JsonResponse({'status': 'error', 'message': '该部门下有子部门，无法删除'}, status=400)
            
            # 检查是否有用户
            if department.userprofile_set.exists():
                return JsonResponse({'status': 'error', 'message': '该部门下有用户，无法删除'}, status=400)
            
            department.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': '部门删除成功'
            })
            
        except Department.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '部门不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in DepartmentAPI.delete: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class PositionAPI(View):
    """职位管理API"""
    
    def get(self, request, position_id=None):
        """获取职位列表或单个职位"""
        try:
            from system.models import Position
            
            if position_id:
                # 获取单个职位
                position = Position.objects.get(id=position_id)
                position_data = {
                    'id': position.id,
                    'name': position.name,
                    'code': position.code,
                    'department_id': position.department.id,
                    'department_name': position.department.name,
                    'level': position.level,
                    'description': position.description,
                    'is_active': position.is_active,
                    'created_at': position.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': position.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': position_data})
            else:
                # 获取职位列表
                positions = Position.objects.all().select_related('department').order_by('department', 'level', 'name')
                positions_data = []
                for pos in positions:
                    # 计算职位下的用户数量
                    user_count = pos.userprofile_set.count()
                    
                    pos_data = {
                        'id': pos.id,
                        'name': pos.name,
                        'code': pos.code,
                        'department_id': pos.department.id,
                        'department_name': pos.department.name,
                        'level': pos.level,
                        'description': pos.description,
                        'is_active': pos.is_active,
                        'user_count': user_count,
                        'created_at': pos.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    positions_data.append(pos_data)
                
                return JsonResponse({'status': 'success', 'data': positions_data})
                
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '职位不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in PositionAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建新职位"""
        try:
            from system.models import Position, Department
            
            data = json.loads(request.body)
            name = data.get('name')
            code = data.get('code')
            department_id = data.get('department_id')
            description = data.get('description', '')
            
            if not name or not code or not department_id:
                return JsonResponse({'status': 'error', 'message': '职位名称、代码和部门不能为空'}, status=400)
            
            # 检查职位代码是否已存在
            if Position.objects.filter(code=code).exists():
                return JsonResponse({'status': 'error', 'message': '职位代码已存在'}, status=400)
            
            # 获取部门
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '部门不存在'}, status=400)
            
            position = Position.objects.create(
                name=name,
                code=code,
                department=department,
                description=description
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '职位创建成功',
                'data': {
                    'id': position.id,
                    'name': position.name,
                    'code': position.code,
                    'department_id': position.department.id,
                    'department_name': position.department.name,
                    'level': position.level,
                    'description': position.description
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in PositionAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, position_id):
        """更新职位"""
        try:
            from system.models import Position, Department
            
            data = json.loads(request.body)
            position = Position.objects.get(id=position_id)
            
            if 'name' in data:
                position.name = data['name']
            if 'code' in data:
                # 检查代码是否与其他职位冲突
                if Position.objects.filter(code=data['code']).exclude(id=position_id).exists():
                    return JsonResponse({'status': 'error', 'message': '职位代码已存在'}, status=400)
                position.code = data['code']
            if 'department_id' in data:
                try:
                    department = Department.objects.get(id=data['department_id'])
                    position.department = department
                except Department.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': '部门不存在'}, status=400)
            if 'description' in data:
                position.description = data['description']
            if 'is_active' in data:
                position.is_active = data['is_active']
            
            position.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '职位更新成功',
                'data': {
                    'id': position.id,
                    'name': position.name,
                    'code': position.code,
                    'department_id': position.department.id,
                    'department_name': position.department.name,
                    'level': position.level,
                    'description': position.description
                }
            })
            
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '职位不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in PositionAPI.put: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, position_id):
        """删除职位"""
        try:
            from system.models import Position
            
            position = Position.objects.get(id=position_id)
            
            # 检查是否有用户
            if position.userprofile_set.exists():
                return JsonResponse({'status': 'error', 'message': '该职位下有用户，无法删除'}, status=400)
            
            position.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': '职位删除成功'
            })
            
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '职位不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in PositionAPI.delete: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)








# ==================== QC报表通用基类和工具函数 ====================
# QC报表相关代码已移动到 home/views/qc_reports.py
@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class RawSoilStorageView(View):
    def delete(self, request, fnumber=None):
        # 检查用户是否有原土入库编辑权限
        if not user_has_permission(request.user, 'raw_soil_storage_edit'):
            # 渲染美观的403错误页面
            from django.shortcuts import render
            context = {
                'user': request.user,
                'request_path': request.path,
                'permission_code': 'raw_soil_storage_edit'
            }
            return render(request, '403.html', context, status=403)
        
        if not fnumber:
            return JsonResponse({'success': False, 'message': '缺少单据编号'})
        eas_host = settings.EAS_API_HOST
        eas_path = settings.EAS_API_PATH_DELETE
        url = eas_host + eas_path
        try:
            resp = requests.post(url, json={'number': fnumber}, timeout=10)
            data = resp.json()
            msg = data.get('msg', '')
            if data.get('code') == 0 or '删除成功' in msg:
                return JsonResponse({'success': True, 'message': msg or '删除成功'})
            else:
                return JsonResponse({'success': False, 'message': msg or '删除失败'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    def get(self, request, fnumber=None):
        # 检查用户是否有原土入库查看权限
        from django.shortcuts import render
        
        # 添加移动端调试日志
        logger = logging.getLogger(__name__)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent
        is_wechat = 'micromessenger' in user_agent or 'wxwork' in user_agent
        
        logger.info(f"=== 原土入库访问调试 ===")
        logger.info(f"用户: {request.user.username}")
        logger.info(f"用户认证状态: {request.user.is_authenticated}")
        logger.info(f"会话ID: {request.session.session_key}")
        logger.info(f"User-Agent: {user_agent[:100]}...")
        logger.info(f"是否移动端: {is_mobile}")
        logger.info(f"是否企业微信: {is_wechat}")
        
        if not user_has_permission(request.user, 'raw_soil_storage_view'):
            logger.warning(f"用户 {request.user.username} 没有原土入库查看权限")
            # 渲染美观的403错误页面
            from django.shortcuts import render
            context = {
                'user': request.user,
                'request_path': request.path,
                'permission_code': 'raw_soil_storage_view'
            }
            return render(request, '403.html', context, status=403)
        
        logger.info(f"用户 {request.user.username} 权限检查通过")
        
        logger = logging.getLogger(__name__)
        if fnumber:
            # --- 原edit_view逻辑 ---
            eas_host = settings.EAS_API_HOST
            eas_path = settings.EAS_API_PATH_GET
            url = eas_host + eas_path
            
            # 检查是否为特殊用户
            special_users = ['GaoBieKeLe', 'JinShui']
            logger.info(f"current user: {request.user.username}")
            
            is_special_user = request.user.username in special_users
            
            record = None
            
            if is_special_user:
                # 特殊用户：遍历所有库存组织+仓库组合查找目标单据
                
                logger.info(f"特殊用户 {request.user.username} 查找单据: {fnumber}")
                
                try:
                    # 获取所有操作对象配置
                    operation_objects = OperationObject.objects.select_related(
                        'inventory_org', 'warehouse'
                    ).all()
                    logger.info(f"operation objects: {operation_objects}")
                    # 设置查询日期范围（最近1个月）
                    today = date.today()
                    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")
                    
                    for operation_object in operation_objects:
                        org_code = operation_object.inventory_org.org_code
                        warehouse_code = operation_object.warehouse.warehouse_code
                        
                        logger.info(f"特殊用户查询组织: {org_code}, 仓库: {warehouse_code}")
                        
                        # 构造完整查询参数，包含日期范围
                        payload = {
                            "orgNumber": org_code,
                            "page": 1,
                            "pageNum": 300,
                            "WarehouseNumber": warehouse_code,
                            "bizDateStart": start_date,
                            "bizDateEnd": end_date,
                            "FNumber": fnumber
                        }
                        
                        try:
                            resp = requests.post(url, json=payload, timeout=10)
                            data = resp.json()
                            
                            if data.get('success') == 'true' and data.get('sysnList'):
                                for item in data['sysnList']:
                                    if item.get('FNumber') == fnumber:
                                        logger.info(f"特殊用户找到单据: {fnumber} 在组织 {org_code} 仓库 {warehouse_code}")
                                        record = self._process_record_item(item, request)
                                        break
                                
                                if record:
                                    break
                        except Exception as e:
                            logger.error(f"特殊用户查询组织 {org_code} 仓库 {warehouse_code} 失败: {str(e)}")
                            continue
                    
                    if not record:
                        logger.warning(f"特殊用户未找到单据: {fnumber}")
                        
                except Exception as e:
                    logger.error(f"特殊用户查询失败: {str(e)}")
            else:
                # 普通用户：使用自己的操作对象配置查询
                try:
                    # 获取用户的操作对象配置
                    operation_object = OperationObject.objects.get(user_id=request.user.username)
                    org_code = operation_object.inventory_org.org_code
                    warehouse_code = operation_object.warehouse.warehouse_code
                    
                    logger = logging.getLogger(__name__)
                    logger.info(f"普通用户 {request.user.username} 查询组织: {org_code}, 仓库: {warehouse_code}")
                    
                    # 设置查询日期范围（最近1个月）
                    today = date.today()
                    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")
                    
                    # 构造完整查询参数
                    payload = {
                        "orgNumber": org_code,
                        "page": 1,
                        "pageNum": 300,
                        "WarehouseNumber": warehouse_code,
                        "bizDateStart": start_date,
                        "bizDateEnd": end_date,
                        "FNumber": fnumber
                    }
                    
                    resp = requests.post(url, json=payload, timeout=10)
                    data = resp.json()
                    if data.get('success') == 'true' and data.get('sysnList'):
                        for item in data['sysnList']:
                            if item.get('FNumber') == fnumber:
                                logger.info(f"普通用户找到单据: {fnumber}")
                                record = self._process_record_item(item, request)
                                break
                except OperationObject.DoesNotExist:
                    logger.error(f"普通用户 {request.user.username} 未配置操作对象")
                except Exception as e:
                    logger.error(f"普通用户查询失败: {str(e)}")
            from django.shortcuts import render
            if not record:

                return render(request, '404.html', {'message': '未找到该单据编号的原土入库记录'})
            
            materials = list(
                MaterialMapping.objects.all().order_by('material_code').values('material_code', 'material_name'))
            
            # 添加菜单数据
            filtered_menu_items = filter_menu_by_permission(MENU_ITEMS, request.user.username)
            
            return render(request, 'production/raw_soil_storage_edit.html',
                          {'record': record, 'materials': materials, 'user': request.user, 'menu_items': filtered_menu_items})
        else:
            # --- 原get逻辑 ---
            context = {
                'current_date': date.today(),
                'user': {
                    'name': request.user.first_name or request.user.username
                }
            }
            materials = MaterialMapping.objects.all().order_by('material_code')
            context['materials'] = [{
                'code': material.material_code,
                'name': material.material_name
            } for material in materials]
            try:
                operation_object = OperationObject.objects.get(user_id=request.user.username)
                context.update({
                    'operation_object': {
                        'inventory_org': {
                            'code': operation_object.inventory_org.org_code,
                            'name': operation_object.inventory_org.org_name
                        },
                        'warehouse': {
                            'code': operation_object.warehouse.warehouse_code,
                            'name': operation_object.warehouse.warehouse_name
                        },
                        'cost_center': {
                            'code': operation_object.cost_center.cost_center_code,
                            'name': operation_object.cost_center.cost_center_name
                        },
                        'cost_object': {
                            'code': operation_object.cost_object.cost_object_code,
                            'name': operation_object.cost_object.cost_object_name
                        },
                        'rate': operation_object.rate
                    }
                })
            except OperationObject.DoesNotExist:
                pass
            # 添加菜单数据
            filtered_menu_items = filter_menu_by_permission(MENU_ITEMS, request.user.username)
            context['menu_items'] = filtered_menu_items
            
            return render(request, 'production/raw_soil_storage.html', context)

    def post(self, request):
        # 检查用户是否有原土入库编辑权限
        if not user_has_permission(request.user, 'raw_soil_storage_edit'):
            # 渲染美观的403错误页面
            from django.shortcuts import render
            context = {
                'user': request.user,
                'request_path': request.path,
                'permission_code': 'raw_soil_storage_edit'
            }
            return render(request, '403.html', context, status=403)
        
        try:
            # 直接使用请求体作为数据
            data = json.loads(request.body)
            
            # 获取用户的操作对象信息
            try:
                operation_object = OperationObject.objects.get(user_id=request.user.username)
            except OperationObject.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户操作对象配置不存在，请联系管理员'
                }, status=400)
            
            # 计算扣水后的实际数量
            quantity = float(data.get('quantity', 0))
            rate = float(operation_object.rate)
            if rate > 1:
                rate = rate / 100.0  # 转换为小数
            actual_quantity = round(quantity * (1 - rate), 2) if rate < 1 else quantity
            
            # 转换为EAS API需要的格式
            eas_data = {
                "bizDate": data.get('bizDate'),
                "costCenterOrgUnit": operation_object.cost_center.cost_center_code,
                "storageOrgUnit": operation_object.inventory_org.org_code,
                "description": data.get('remark', ''),
                "entry": [{
                    "seq": 1,
                    "material": data.get('materialName'),
                    "costObject": operation_object.cost_object.cost_object_code,
                    "qty": actual_quantity,
                    "ckno": operation_object.warehouse.warehouse_code,
                    "Lot": data.get('lot', '')
                }]
            }

            # 发送请求到 EAS API
            eas_api_host = settings.EAS_API_HOST
            eas_api_path = settings.EAS_API_PATH_ADD
            url = f"{eas_api_host}{eas_api_path}"
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"发送到EAS API的数据: {eas_data}")
            
            response = requests.post(
                url,
                json=eas_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            logger.info(f"EAS API返回状态码: {response.status_code}")
            logger.info(f"EAS API返回内容: {response.text}")

            # 处理EAS API的响应
            try:
                result = response.json()
                logger.info(f"EAS API返回JSON: {result}")

                if result['code'] == 'null':
                    return JsonResponse({
                            'success': False,
                            'message': f'提交失败: {str(result['msg'])}'
            }, status=400)
                return JsonResponse(result)
            except:
                # 如果不是JSON格式，返回文本内容
                return JsonResponse({
                    'success': True,
                    'message': '数据提交成功',
                    'raw_response': response.text
                })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"原土入库提交失败: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'提交失败: {str(e)}'
            }, status=400)

    def _process_record_item(self, item, request):
        """处理记录项，提取所需字段"""
        entry = item.get('entry', [{}])[0]
        try:
            inventory_org_name = InventoryOrg.objects.get(
                org_code=item.get('storageOrgUnitNumber')).org_name
        except:
            inventory_org_name = ''
        try:
            cost_center_name = CostCenterMapping.objects.get(
                cost_center_code=item.get('costCenterOrgUnitNumber')).cost_center_name
        except:
            cost_center_name = ''
        try:
            material_name = MaterialMapping.objects.get(
                material_code=entry.get('materialNumber')).material_name
        except:
            material_name = ''
        try:
            cost_object_name = CostObjectMapping.objects.get(
                cost_object_code=entry.get('CostObjectNumber')).cost_object_name
        except:
            cost_object_name = ''
        try:
            warehouse_name = WarehouseMapping.objects.get(
                warehouse_code=entry.get('WarehouseNumber')).warehouse_name
        except:
            warehouse_name = ''
        
        # 检查是否为特殊用户，如果是则获取对应库存组织的扣水率
        special_users = ['GaoBieKeLe', 'JinShui']
        is_special_user = request.user.username in special_users
        
        if is_special_user:
            # 特殊用户：根据库存组织获取扣水率
            try:
                from .models import WaterDeductionRate
                water_deduction_rate = WaterDeductionRate.objects.get(
                    inventory_org__org_code=item.get('storageOrgUnitNumber')
                )
                rate = water_deduction_rate.rate
                logger = logging.getLogger(__name__)
                logger.info(f"特殊用户 {request.user.username} 获取库存组织 {item.get('storageOrgUnitNumber')} 的扣水率: {rate}")
            except WaterDeductionRate.DoesNotExist:
                rate = 0
                logger = logging.getLogger(__name__)
                logger.warning(f"特殊用户 {request.user.username} 的库存组织 {item.get('storageOrgUnitNumber')} 未配置扣水率，使用默认值0")
        else:
            # 普通用户：使用操作对象的扣水率
            try:
                operation_object = OperationObject.objects.get(user_id=request.user.username)
                rate = operation_object.rate
            except:
                rate = ''
        
        record = {
            'fnumber': item.get('FNumber'),
            'bizDate': item.get('FBizDate'),
            'costCenterOrgUnit': item.get('costCenterOrgUnitNumber'),
            'costCenterOrgUnitName': cost_center_name,
            'storageOrgUnit': item.get('storageOrgUnitNumber'),
            'storageOrgUnitName': inventory_org_name,
            'materialNumber': entry.get('materialNumber'),
            'materialName': material_name,
            'costObject': entry.get('CostObjectNumber'),
            'costObjectName': cost_object_name,
            'quantity': entry.get('FQty'),
            'ckno': entry.get('WarehouseNumber'),
            'warehouseName': warehouse_name,
            'Lot': entry.get('FLot'),
            'rate': rate,
        }
        
        try:
            qty = float(record['quantity'])
            r = float(rate)
            if r > 1:
                r = r / 100.0
            record['quantity_adjusted'] = round(qty / (1 - r), 2) if r < 1 else qty
            record['remark'] = f"真实入库数量：{record['quantity_adjusted']}*(1-{r})={round(float(record['quantity_adjusted']) * (1 - r), 2) if record['quantity_adjusted'] != '' and r < 1 else ''}"
        except:
            record['quantity_adjusted'] = record['quantity']
            record['remark'] = item.get('description', '')
        
        try:
            qty = float(record['quantity'])
            r = float(rate)
            if r > 1:
                r = r / 100.0
            record['quantity_adjusted'] = round(qty / (1 - r), 2) if r < 1 else qty
        except:
            record['quantity_adjusted'] = record['quantity']
        
        return record

    def put(self, request, fnumber):
        # 检查用户是否有原土入库编辑权限
        if not user_has_permission(request.user, 'raw_soil_storage_edit'):
            # 渲染美观的403错误页面
            from django.shortcuts import render
            context = {
                'user': request.user,
                'request_path': request.path,
                'permission_code': 'raw_soil_storage_edit'
            }
            return render(request, '403.html', context, status=403)
        
        if not fnumber or str(fnumber).strip() == '':
            return JsonResponse({
                'success': False,
                'message': '单据编号（fnumber）不能为空'
            }, status=400)
        try:
            import requests
            from datetime import datetime
            import logging
            data = json.loads(request.body)
            logger = logging.getLogger(__name__)
            logger.debug(f"Received PUT request for fnumber: {fnumber}, data: {data}")
            # 组装body，字段映射
            # 真实入库数量 = 数量 * (1 - 扣水率)
            raw_qty = data.get("quantity")
            actual_date = data.get("date")
            logger.info(f"Received PUT request for fnumber: {fnumber}, data: {data}")
            logger.debug(f"Raw quantity: {raw_qty}")
            logger.debug(f"Raw rate: {data.get('rate')}")

            rate = data.get("rate")
            if rate is None:
                # 检查是否为特殊用户，如果是则获取对应库存组织的扣水率
                special_users = ['GaoBieKeLe', 'JinShui', 'geobiekele', 'jinshui']
                is_special_user = request.user.username in special_users
                
                if is_special_user:
                    # 特殊用户：需要从请求中获取库存组织信息来查询扣水率
                    try:
                        # 获取原始记录信息
                        eas_host = settings.EAS_API_HOST
                        eas_path = settings.EAS_API_PATH_GET
                        url = eas_host + eas_path
                        
                        # 构造查询请求
                        payload = {
                            "orgNumber": "YT0110",  # 默认值，实际应该从记录中获取
                            "page": 1,
                            "pageNum": 300,
                            "WarehouseNumber": "DT08",  # 默认值，实际应该从记录中获取
                            "FNumber": fnumber
                        }
                        
                        resp = requests.post(url, json=payload, timeout=10)
                        data_response = resp.json()
                        records = data_response.get('sysnList') or data_response.get('data') or []
                        
                        if records:
                            for item in records:
                                if item.get('FNumber') == fnumber:
                                    storage_org_code = item.get('storageOrgUnitNumber')
                                    if storage_org_code:
                                        try:
                                            from .models import WaterDeductionRate
                                            water_deduction_rate = WaterDeductionRate.objects.get(
                                                inventory_org__org_code=storage_org_code
                                            )
                                            rate = water_deduction_rate.rate
                                            logger.info(f"特殊用户 {request.user.username} 编辑时获取库存组织 {storage_org_code} 的扣水率: {rate}")
                                        except WaterDeductionRate.DoesNotExist:
                                            rate = 0
                                            logger.warning(f"特殊用户 {request.user.username} 编辑时库存组织 {storage_org_code} 未配置扣水率，使用默认值0")
                                    else:
                                        rate = 0
                                    break
                            else:
                                rate = 0
                        else:
                            rate = 0
                    except Exception as e:
                        logger.error(f"特殊用户 {request.user.username} 编辑时获取扣水率失败: {str(e)}")
                        rate = 0
                else:
                    # 普通用户：使用操作对象的扣水率
                    try:
                        operation_object = OperationObject.objects.get(user_id=request.user.username)
                        rate = operation_object.rate
                    except OperationObject.DoesNotExist:
                        rate = 0
            try:
                qty = float(raw_qty)
                r = float(rate)
                logger.debug(f"Quantity: {qty}, Rate: {r}")
                if r > 1:
                    r = r / 100.0
                real_qty = round(qty * (1 - r), 2)
                # logger.debug(f"Real quantity: {real_qty}")
            except Exception as e:
                logger.error(f"Failed to calculate real quantity: {str(e)}")
                real_qty = raw_qty
            logger.debug(f"Real quantity: {real_qty}")
            body = {
                "fnumber": fnumber,
                "bizDate": actual_date,
                "costCenterOrgUnit": data.get('costCenterOrgUnit', ''),
                "storageOrgUnit": data.get('storageOrgUnit', ''),
                "description": data.get('description', ''),
                "entry": [{
                    "seq": 1,
                    "material": data.get('materialNumber', ''),
                    "costObject": data.get('costObject', ''),
                    "qty": real_qty,
                    "ckno": data.get('warehouseNumber', ''),
                    "Lot": data.get('lot', '')
                }]
            }
            logger.debug(f"Sending PUT request to EAS with body: {body}")
            url = settings.EAS_API_HOST + settings.EAS_API_PATH_UPDATE
            response = requests.post(url, json=body, headers={'Content-Type': 'application/json'})
            try:
                resp_json = response.json()
            except Exception:
                resp_json = {"success": False, "message": "EAS返回非JSON格式", "raw": response.text}
            return JsonResponse(resp_json)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating raw soil storage: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


class IndexView(View):
    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)

        # 处理企业微信回调
        code = request.GET.get('code')
        if code:
            logger.info(f'Processing WeChat callback with code: {code}')
            # Processing WeChat callback with code: code
            # 重定向到企业微信回调URL
            from wechat_auth.views import WeChatCallbackView
            return WeChatCallbackView.as_view()(request)

        # 如果用户已登录，重定向到home
        if request.user.is_authenticated:
            logger.info(f'User {request.user.username} is authenticated, redirecting to home')
            # User request.user.username is authenticated, redirecting to home
            return redirect('home')

        # 检测是否在企业微信内
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_wechat_work = 'wxwork' in user_agent or ('micromessenger' in user_agent and 'wxwork' in user_agent)
        
        # 如果在企业微信内且未登录，自动跳转到登录（会自动使用OAuth2授权）
        if is_wechat_work:
            logger.info('User is in WeChat Work but not authenticated, redirecting to auto login')
            return redirect('login')
        
        # 未登录用户重定向到登录页面
        logger.info('Redirecting unauthenticated user to login')
        # Redirecting unauthenticated user to login
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)

        # 添加用户认证状态调试信息
        logger.info(
            f'HomeView accessed by user: {request.user.username if request.user.is_authenticated else "Anonymous"}')
        logger.info(f'User is_authenticated: {request.user.is_authenticated}')
        logger.info(f'Session key: {request.session.session_key}')

        # 检测是否为移动设备
        is_mobile = False
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            is_mobile = True

        # 根据用户权限过滤菜单
        filtered_menu_items = filter_menu_by_permission(MENU_ITEMS, request.user.username)

        return render(request, 'home.html', {
            'user': request.user,
            'menu_items': filtered_menu_items,
            'is_mobile': is_mobile
        })





@method_decorator(login_required, name='dispatch')
class UserAPI(View):
    def get(self, request):
        userid = request.user.username
        department = request.user.last_name  # 部门名称
        name = request.user.first_name  # 真实姓名

        # User info - ID: userid, Department: department, Name: name

        return JsonResponse({
            'errcode': 0,
            'user_id': userid,
            'department': department,
            'name': name,
            'is_admin': is_admin_user(userid)
        })
@require_GET
@system_settings_required
def get_parameter(request, param_id):
    """获取单个参数值"""
    try:
        parameter = Parameter.objects.get(id=param_id)
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': parameter.id,
                'name': parameter.name,
                'value': parameter.value,
                'description': parameter.description
            }
        })
    except Parameter.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '参数不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_GET
@login_required
def get_report_parameter(request, param_id):
    """获取报表参数值（不需要系统设置权限）"""
    try:
        parameter = Parameter.objects.get(id=param_id)
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': parameter.id,
                'name': parameter.name,
                'value': parameter.value,
                'description': parameter.description
            }
        })
    except Parameter.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '参数不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# 在文件末尾添加初始化参数的函数
def init_parameters():
    """初始化系统参数"""
    default_parameters = [
        {
            'id': 'report_edit_limit',
            'name': '报表编辑期限',
            'value': '7',
            'description': '设置报表可编辑的天数限制，超过此天数的报表将不能编辑和删除',
            'group': '报表参数'
        }
    ]

    for param in default_parameters:
        Parameter.objects.get_or_create(
            id=param['id'],
            defaults={
                'name': param['name'],
                'value': param['value'],
                'description': param['description'],
                'group': param['group']
            }
        )


# 在应用启动时初始化参数
init_parameters()

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class MaterialMappingAPI(View):
    def get(self, request):
        try:
            materials = MaterialMapping.objects.all()
            data = [{
                'id': material.id,
                'material_code': material.material_code,
                'material_name': material.material_name,
                'created_at': material.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for material in materials]
            return JsonResponse({
                'status': 'success',
                'data': data
            })
        except Exception as e:
            logger.error(f'Error fetching materials: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request):
        try:
            logger.info('Received POST request for material mapping')
            data = json.loads(request.body)
            logger.info(f'Received data: {data}')

            material = MaterialMapping.objects.create(
                material_code=data['material_code'],
                material_name=data['material_name']
            )
            logger.info(f'Created material mapping with ID: {material.id}')

            response_data = {
                'id': material.id,
                'material_code': material.material_code,
                'material_name': material.material_name,
                'created_at': material.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            logger.info(f'Sending response: {response_data}')
            return JsonResponse({
                'status': 'success',
                'data': response_data
            })
        except json.JSONDecodeError as e:
            logger.error(f'JSON decode error: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except KeyError as e:
            logger.error(f'Missing required field: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': f'Missing required field: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.error(f'Error creating material mapping: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    def put(self, request, material_id):
        try:
            data = json.loads(request.body)
            material = MaterialMapping.objects.get(id=material_id)
            material.material_code = data['material_code']
            material.material_name = data['material_name']
            material.save()
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': material.id,
                    'material_code': material.material_code,
                    'material_name': material.material_name,
                    'created_at': material.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except MaterialMapping.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '物料映射不存在'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, material_id):
        try:
            logger.info(f'Attempting to delete material mapping with ID: {material_id}')
            material = MaterialMapping.objects.get(id=material_id)
            material.delete()
            logger.info(f'Successfully deleted material mapping with ID: {material_id}')
            return JsonResponse({
                'status': 'success',
                'data': None,
                'message': '删除成功'
            })
        except MaterialMapping.DoesNotExist:
            logger.warning(f'Attempted to delete non-existent material mapping with ID: {material_id}')
            return JsonResponse({
                'status': 'error',
                'message': '物料映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error deleting material mapping with ID {material_id}: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class WaterDeductionRateAPI(View):
    def get(self, request):
        try:
            logger.info('开始获取扣水率列表')

            rates = WaterDeductionRate.objects.select_related('inventory_org').all().order_by('-created_at')

            data = [{
                'id': rate.id,
                'inventory_org_id': rate.inventory_org.id,
                'inventory_org_name': rate.inventory_org.org_name,
                'rate': str(rate.rate),
                'created_at': rate.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': rate.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            } for rate in rates]

            logger.info('扣水率列表获取成功')
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f'获取扣水率列表失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        try:
            logger.info('开始处理新增扣水率请求')
            data = json.loads(request.body)

            inventory_org_id = data.get('inventory_org_id')
            rate = data.get('rate')

            if not inventory_org_id or rate is None:
                return JsonResponse({'error': '库存组织和扣水率不能为空'}, status=400)

            try:
                rate_decimal = Decimal(str(rate))
                if rate_decimal < 0 or rate_decimal > 100:
                    return JsonResponse({'error': '扣水率必须在0到100之间'}, status=400)
            except InvalidOperation:
                return JsonResponse({'error': '无效的扣水率数值'}, status=400)

            try:
                inventory_org = InventoryOrg.objects.get(id=inventory_org_id)
            except InventoryOrg.DoesNotExist:
                return JsonResponse({'error': '库存组织不存在'}, status=404)

            if WaterDeductionRate.objects.filter(inventory_org=inventory_org).exists():
                return JsonResponse({'error': '该库存组织已设置扣水率'}, status=400)

            rate_obj = WaterDeductionRate.objects.create(
                inventory_org=inventory_org,
                rate=rate_decimal
            )

            return JsonResponse({
                'id': rate_obj.id,
                'inventory_org_id': rate_obj.inventory_org.id,
                'inventory_org_name': rate_obj.inventory_org.org_name,
                'rate': str(rate_obj.rate),
                'created_at': rate_obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': rate_obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            logger.error(f'新增扣水率失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def put(self, request, rate_id):
        try:
            logger.info(f'开始处理更新扣水率请求 - ID: {rate_id}')
            data = json.loads(request.body)

            try:
                rate_obj = WaterDeductionRate.objects.get(id=rate_id)
            except WaterDeductionRate.DoesNotExist:
                return JsonResponse({'error': '扣水率记录不存在'}, status=404)

            rate = data.get('rate')
            if rate is None:
                return JsonResponse({'error': '扣水率不能为空'}, status=400)

            try:
                rate_decimal = Decimal(str(rate))
                if rate_decimal < 0 or rate_decimal > 100:
                    return JsonResponse({'error': '扣水率必须在0到100之间'}, status=400)
            except InvalidOperation:
                return JsonResponse({'error': '无效的扣水率数值'}, status=400)

            rate_obj.rate = rate_decimal
            rate_obj.save()

            return JsonResponse({
                'id': rate_obj.id,
                'inventory_org_id': rate_obj.inventory_org.id,
                'inventory_org_name': rate_obj.inventory_org.org_name,
                'rate': str(rate_obj.rate),
                'created_at': rate_obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': rate_obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            logger.error(f'更新扣水率失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, rate_id):
        try:
            logger.info(f'开始处理删除扣水率请求 - ID: {rate_id}')

            try:
                rate_obj = WaterDeductionRate.objects.get(id=rate_id)
            except WaterDeductionRate.DoesNotExist:
                return JsonResponse({'error': '扣水率记录不存在'}, status=404)

            rate_obj.delete()
            return JsonResponse({'message': '扣水率删除成功'})
        except Exception as e:
            logger.error(f'删除扣水率失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class InventoryOrgAPI(View):
    def get(self, request):
        try:
            logger.info('开始获取库存组织列表')
            orgs = InventoryOrg.objects.all().order_by('-created_at')
            logger.debug(f'查询到 {orgs.count()} 条库存组织记录')

            data = [{
                'id': org.id,
                'org_name': org.org_name,
                'org_code': org.org_code,
                'created_at': org.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for org in orgs]

            logger.info('库存组织列表查询成功')
            logger.debug(f'返回数据: {data}')
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f'获取库存组织列表失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        try:
            logger.info('开始处理新增库存组织请求')
            logger.debug(f'接收到的请求体: {request.body.decode()}')

            data = json.loads(request.body)
            org_name = data.get('org_name')
            org_code = data.get('org_code')

            logger.debug(f'解析的数据 - 组织名称: {org_name}, 组织编码: {org_code}')

            if not org_name or not org_code:
                logger.warning('组织名称或组织编码为空')
                return JsonResponse({'error': '组织名称和组织编码不能为空'}, status=400)

            # 检查组织编码是否已存在
            if InventoryOrg.objects.filter(org_code=org_code).exists():
                logger.warning(f'组织编码 {org_code} 已存在')
                return JsonResponse({'error': '组织编码已存在'}, status=400)

            # 创建新的库存组织
            org = InventoryOrg.objects.create(
                org_name=org_name,
                org_code=org_code
            )
            logger.info(f'成功创建库存组织 - ID: {org.id}')

            response_data = {
                'id': org.id,
                'org_name': org.org_name,
                'org_code': org.org_code,
                'created_at': org.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            logger.debug(f'返回数据: {response_data}')
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            logger.error(f'JSON解析错误: {str(e)}', exc_info=True)
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'创建库存组织失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def put(self, request, org_id):
        try:
            logger.info(f'开始处理更新库存组织请求 - ID: {org_id}')
            logger.debug(f'接收到的请求体: {request.body.decode()}')

            data = json.loads(request.body)
            org = InventoryOrg.objects.get(id=org_id)
            logger.debug(f'找到待更新的库存组织: {org.org_name} ({org.org_code})')

            org_name = data.get('org_name')
            org_code = data.get('org_code')
            logger.debug(f'更新数据 - 新组织名称: {org_name}, 新组织编码: {org_code}')

            if not org_name or not org_code:
                logger.warning('组织名称或组织编码为空')
                return JsonResponse({'error': '组织名称和组织编码不能为空'}, status=400)

            # 检查新的组织编码是否已存在（排除当前记录）
            if InventoryOrg.objects.filter(org_code=org_code).exclude(id=org_id).exists():
                logger.warning(f'组织编码 {org_code} 已被其他组织使用')
                return JsonResponse({'error': '组织编码已存在'}, status=400)

            # 记录更新前的值
            old_name = org.org_name
            old_code = org.org_code

            org.org_name = org_name
            org.org_code = org_code
            org.save()

            logger.info(f'成功更新库存组织 - ID: {org.id}')
            logger.debug(f'更新详情 - 名称: {old_name} -> {org_name}, 编码: {old_code} -> {org_code}')

            response_data = {
                'id': org.id,
                'org_name': org.org_name,
                'org_code': org.org_code,
                'created_at': org.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            logger.debug(f'返回数据: {response_data}')
            return JsonResponse(response_data)

        except InventoryOrg.DoesNotExist:
            logger.error(f'库存组织不存在 - ID: {org_id}')
            return JsonResponse({'error': '库存组织不存在'}, status=404)
        except json.JSONDecodeError as e:
            logger.error(f'JSON解析错误: {str(e)}', exc_info=True)
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'更新库存组织失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, org_id):
        try:
            logger.info(f'开始处理删除库存组织请求 - ID: {org_id}')

            org = InventoryOrg.objects.get(id=org_id)
            logger.debug(f'找到待删除的库存组织: {org.org_name} ({org.org_code})')

            org.delete()
            logger.info(f'成功删除库存组织 - ID: {org_id}')

            return JsonResponse({'status': 'success'})
        except InventoryOrg.DoesNotExist:
            logger.error(f'库存组织不存在 - ID: {org_id}')
            return JsonResponse({'error': '库存组织不存在'}, status=404)
        except Exception as e:
            logger.error(f'删除库存组织失败: {str(e)}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class WarehouseMappingAPI(View):
    def get(self, request):
        try:
            warehouses = WarehouseMapping.objects.all()
            data = [{
                'id': warehouse.id,
                'warehouse_code': warehouse.warehouse_code,
                'warehouse_name': warehouse.warehouse_name,
                'created_at': warehouse.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for warehouse in warehouses]
            return JsonResponse({
                'status': 'success',
                'data': data
            })
        except Exception as e:
            logger.error(f'Error fetching warehouses: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            warehouse = WarehouseMapping.objects.create(
                warehouse_code=data['warehouse_code'],
                warehouse_name=data['warehouse_name']
            )
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': warehouse.id,
                    'warehouse_code': warehouse.warehouse_code,
                    'warehouse_name': warehouse.warehouse_name,
                    'created_at': warehouse.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            logger.error(f'Error creating warehouse: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def put(self, request, warehouse_id):
        try:
            data = json.loads(request.body)
            warehouse = WarehouseMapping.objects.get(id=warehouse_id)
            warehouse.warehouse_code = data['warehouse_code']
            warehouse.warehouse_name = data['warehouse_name']
            warehouse.save()
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': warehouse.id,
                    'warehouse_code': warehouse.warehouse_code,
                    'warehouse_name': warehouse.warehouse_name,
                    'created_at': warehouse.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except WarehouseMapping.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '仓库映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error updating warehouse: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def delete(self, request, warehouse_id):
        try:
            logger.info(f'Attempting to delete warehouse mapping with ID: {warehouse_id}')
            warehouse = WarehouseMapping.objects.get(id=warehouse_id)
            warehouse.delete()
            logger.info(f'Successfully deleted warehouse mapping with ID: {warehouse_id}')
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except WarehouseMapping.DoesNotExist:
            logger.warning(f'Warehouse mapping with ID {warehouse_id} not found')
            return JsonResponse({
                'status': 'error',
                'message': '仓库映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error deleting warehouse mapping with ID {warehouse_id}: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class CostCenterMappingAPI(View):
    def get(self, request):
        try:
            cost_centers = CostCenterMapping.objects.all()
            data = [{
                'id': cost_center.id,
                'cost_center_code': cost_center.cost_center_code,
                'cost_center_name': cost_center.cost_center_name,
                'created_at': cost_center.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for cost_center in cost_centers]
            return JsonResponse({
                'status': 'success',
                'data': data
            })
        except Exception as e:
            logger.error(f'Error fetching cost centers: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            cost_center = CostCenterMapping.objects.create(
                cost_center_code=data['cost_center_code'],
                cost_center_name=data['cost_center_name']
            )
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': cost_center.id,
                    'cost_center_code': cost_center.cost_center_code,
                    'cost_center_name': cost_center.cost_center_name,
                    'created_at': cost_center.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            logger.error(f'Error creating cost center: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def put(self, request, cost_center_id):
        try:
            data = json.loads(request.body)
            cost_center = CostCenterMapping.objects.get(id=cost_center_id)
            cost_center.cost_center_code = data['cost_center_code']
            cost_center.cost_center_name = data['cost_center_name']
            cost_center.save()
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': cost_center.id,
                    'cost_center_code': cost_center.cost_center_code,
                    'cost_center_name': cost_center.cost_center_name,
                    'created_at': cost_center.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except CostCenterMapping.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '成本中心映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error updating cost center: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def delete(self, request, cost_center_id):
        try:
            logger.info(f'Attempting to delete cost center mapping with ID: {cost_center_id}')
            cost_center = CostCenterMapping.objects.get(id=cost_center_id)
            cost_center.delete()
            logger.info(f'Successfully deleted cost center mapping with ID: {cost_center_id}')
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except CostCenterMapping.DoesNotExist:
            logger.warning(f'Cost center mapping with ID {cost_center_id} not found')
            return JsonResponse({
                'status': 'error',
                'message': '成本中心映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error deleting cost center mapping with ID {cost_center_id}: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class CostObjectMappingAPI(View):
    def get(self, request):
        try:
            cost_objects = CostObjectMapping.objects.all()
            data = [{
                'id': cost_object.id,
                'cost_object_code': cost_object.cost_object_code,
                'cost_object_name': cost_object.cost_object_name,
                'created_at': cost_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for cost_object in cost_objects]
            return JsonResponse({
                'status': 'success',
                'data': data
            })
        except Exception as e:
            logger.error(f'Error fetching cost objects: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            cost_object = CostObjectMapping.objects.create(
                cost_object_code=data['cost_object_code'],
                cost_object_name=data['cost_object_name']
            )
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': cost_object.id,
                    'cost_object_code': cost_object.cost_object_code,
                    'cost_object_name': cost_object.cost_object_name,
                    'created_at': cost_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            logger.error(f'Error creating cost object: {str(e)}')  # 记录错误
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def put(self, request, cost_object_id):
        try:
            data = json.loads(request.body)
            cost_object = CostObjectMapping.objects.get(id=cost_object_id)
            cost_object.cost_object_code = data['cost_object_code']
            cost_object.cost_object_name = data['cost_object_name']
            cost_object.save()
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': cost_object.id,
                    'cost_object_code': cost_object.cost_object_code,
                    'cost_object_name': cost_object.cost_object_name,
                    'created_at': cost_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except CostObjectMapping.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '成本对象映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error updating cost object: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def delete(self, request, cost_object_id):
        try:
            cost_object = CostObjectMapping.objects.get(id=cost_object_id)
            cost_object.delete()
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except CostObjectMapping.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '成本对象映射不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error deleting cost object mapping with ID {cost_object_id}: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class OperationObjectAPI(View):
    def get(self, request, object_id=None):
        try:
            # 获取单个操作对象
            if object_id is None:
                operation_objects = OperationObject.objects.select_related(
                    'inventory_org', 'warehouse', 'cost_center', 'cost_object'
                ).all()

                data = [{
                    'id': obj.id,
                    'user_id': obj.user_id,
                    'inventory_org': {
                        'id': obj.inventory_org.id,
                        'name': obj.inventory_org.org_name
                    },
                    'warehouse': {
                        'id': obj.warehouse.id,
                        'name': obj.warehouse.warehouse_name
                    },
                    'cost_center': {
                        'id': obj.cost_center.id,
                        'name': obj.cost_center.cost_center_name
                    },
                    'cost_object': {
                        'id': obj.cost_object.id,
                        'name': obj.cost_object.cost_object_name
                    },
                    'rate': str(obj.rate),
                    'created_at': obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
                } for obj in operation_objects]

                return JsonResponse({
                    'status': 'success',
                    'data': data
                })
            else:
                # 获取单个对象
                operation_object = OperationObject.objects.select_related(
                    'inventory_org', 'warehouse', 'cost_center', 'cost_object'
                ).get(id=object_id)

                data = {
                    'id': operation_object.id,
                    'user_id': operation_object.user_id,
                    'inventory_org': {
                        'id': operation_object.inventory_org.id,
                        'name': operation_object.inventory_org.org_name
                    },
                    'warehouse': {
                        'id': operation_object.warehouse.id,
                        'name': operation_object.warehouse.warehouse_name
                    },
                    'cost_center': {
                        'id': operation_object.cost_center.id,
                        'name': operation_object.cost_center.cost_center_name
                    },
                    'cost_object': {
                        'id': operation_object.cost_object.id,
                        'name': operation_object.cost_object.cost_object_name
                    },
                    'rate': str(operation_object.rate),
                    'created_at': operation_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }

                return JsonResponse({
                    'status': 'success',
                    'data': data
                })

        except OperationObject.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '操作对象不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error getting operation object: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)

            # 获取关联对象
            inventory_org = InventoryOrg.objects.get(id=data['inventory_org_id'])
            warehouse = WarehouseMapping.objects.get(id=data['warehouse_id'])
            cost_center = CostCenterMapping.objects.get(id=data['cost_center_id'])
            cost_object = CostObjectMapping.objects.get(id=data['cost_object_id'])

            # 创建操作对象
            operation_object = OperationObject.objects.create(
                user_id=data['user_id'],
                inventory_org=inventory_org,
                warehouse=warehouse,
                cost_center=cost_center,
                cost_object=cost_object,
                rate=data['rate']
            )

            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': operation_object.id,
                    'user_id': operation_object.user_id,
                    'inventory_org': {
                        'id': inventory_org.id,
                        'name': inventory_org.org_name
                    },
                    'warehouse': {
                        'id': warehouse.id,
                        'name': warehouse.warehouse_name
                    },
                    'cost_center': {
                        'id': cost_center.id,
                        'name': cost_center.cost_center_name
                    },
                    'cost_object': {
                        'id': cost_object.id,
                        'name': cost_object.cost_object_name
                    },
                    'rate': str(operation_object.rate),
                    'created_at': operation_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except (InventoryOrg.DoesNotExist, WarehouseMapping.DoesNotExist,
                CostCenterMapping.DoesNotExist, CostObjectMapping.DoesNotExist) as e:
            return JsonResponse({
                'status': 'error',
                'message': '关联对象不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error creating operation object: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def put(self, request, object_id):
        try:
            data = json.loads(request.body)

            # 获取操作对象
            operation_object = OperationObject.objects.get(id=object_id)

            # 获取关联对象
            inventory_org = InventoryOrg.objects.get(id=data['inventory_org_id'])
            warehouse = WarehouseMapping.objects.get(id=data['warehouse_id'])
            cost_center = CostCenterMapping.objects.get(id=data['cost_center_id'])
            cost_object = CostObjectMapping.objects.get(id=data['cost_object_id'])

            # 更新操作对象
            operation_object.inventory_org = inventory_org
            operation_object.warehouse = warehouse
            operation_object.cost_center = cost_center
            operation_object.cost_object = cost_object
            operation_object.rate = data['rate']
            operation_object.save()

            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': operation_object.id,
                    'user_id': operation_object.user_id,
                    'inventory_org': {
                        'id': inventory_org.id,
                        'name': inventory_org.org_name
                    },
                    'warehouse': {
                        'id': warehouse.id,
                        'name': warehouse.warehouse_name
                    },
                    'cost_center': {
                        'id': cost_center.id,
                        'name': cost_center.cost_center_name
                    },
                    'cost_object': {
                        'id': cost_object.id,
                        'name': cost_object.cost_object_name
                    },
                    'rate': str(operation_object.rate),
                    'created_at': operation_object.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except OperationObject.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '操作对象不存在'
            }, status=404)
        except (InventoryOrg.DoesNotExist, WarehouseMapping.DoesNotExist,
                CostCenterMapping.DoesNotExist, CostObjectMapping.DoesNotExist) as e:
            return JsonResponse({
                'status': 'error',
                'message': '关联对象不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error updating operation object: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def delete(self, request, object_id):
        try:
            operation_object = OperationObject.objects.get(id=object_id)
            operation_object.delete()

            return JsonResponse({
                'status': 'success',
                'message': '操作对象删除成功'
            })
        except OperationObject.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '操作对象不存在'
            }, status=404)
        except Exception as e:
            logger.error(f'Error deleting operation object: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


# QC报表相关代码已移动到 home/views/qc_reports.py
@login_required
# QC报表相关代码已移动到 home/views/qc_reports.py
@login_required
@csrf_exempt
@permission_required('qc_report_edit')
# QC报表相关代码已移动到 home/views/qc_reports.py
@login_required
def simple_permission_config(request):
    """简单权限配置页面 - 不需要特殊权限"""
    if request.method == 'POST':
        try:
            from home.models import Parameter
            import json
            
            action = request.POST.get('action')
            
            if action == 'enable_all':
                # 启用跨用户编辑功能
                Parameter.objects.update_or_create(
                    id='enable_cross_user_edit',
                    defaults={'value': 'true'}
                )
                # 为东泰QC报表启用跨用户编辑权限
                permissions = {
                    'view': True,
                    'edit': True,
                    'edit_others': True,
                    'delete': True,
                    'manage': True
                }
                Parameter.objects.update_or_create(
                    id='dongtai_qc_report_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
                return JsonResponse({'status': 'success', 'message': '已启用跨用户编辑功能'})
                
            elif action == 'disable_all':
                # 禁用跨用户编辑功能
                Parameter.objects.update_or_create(
                    id='enable_cross_user_edit',
                    defaults={'value': 'false'}
                )
                return JsonResponse({'status': 'success', 'message': '已禁用跨用户编辑功能'})
                
            elif action == 'update_limit':
                # 更新编辑期限
                edit_limit = request.POST.get('edit_limit', '7')
                Parameter.objects.update_or_create(
                    id='report_edit_limit',
                    defaults={'value': edit_limit}
                )
                return JsonResponse({'status': 'success', 'message': f'已更新编辑期限为 {edit_limit} 天'})
                
            elif action == 'save_detail':
                # 保存详细配置
                cross_user_edit = request.POST.get('enable_cross_user_edit') == 'true'
                dongtai_edit_others = request.POST.get('dongtai_edit_others') == 'true'
                
                Parameter.objects.update_or_create(
                    id='enable_cross_user_edit',
                    defaults={'value': 'true' if cross_user_edit else 'false'}
                )
                
                permissions = {
                    'view': True,
                    'edit': True,
                    'edit_others': dongtai_edit_others,
                    'delete': True,
                    'manage': True
                }
                Parameter.objects.update_or_create(
                    id='dongtai_qc_report_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
                
                return JsonResponse({'status': 'success', 'message': '详细配置已保存'})
            else:
                # 如果没有匹配到任何action，返回错误
                return JsonResponse({'status': 'error', 'message': '无效的操作类型'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'保存失败：{str(e)}'})
    
    # GET请求 - 显示配置页面
    try:
        from home.models import Parameter
        import json
        
        # 获取当前设置
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        cross_user_edit_enabled = cross_edit_param and cross_edit_param.value == 'true'
        
        edit_limit_param = Parameter.objects.filter(id='report_edit_limit').first()
        edit_limit = int(edit_limit_param.value) if edit_limit_param and edit_limit_param.value else 7
        
        # 获取东泰QC报表权限设置
        dongtai_param = Parameter.objects.filter(id='dongtai_qc_report_permissions').first()
        dongtai_edit_others = False
        if dongtai_param and dongtai_param.value:
            try:
                permissions = json.loads(dongtai_param.value)
                dongtai_edit_others = permissions.get('edit_others', False)
            except:
                pass
        
        context = {
            'cross_user_edit_enabled': cross_user_edit_enabled,
            'edit_limit': edit_limit,
            'dongtai_edit_others': dongtai_edit_others
        }
        
        return render(request, 'admin/simple_permission_config.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': f'加载权限配置页面失败：{str(e)}'
        })


@login_required
def debug_user_permissions_page(request):
    """调试用户权限管理页面"""
    return render(request, 'admin/debug_user_permissions.html')

@login_required
def user_permission_guide_page(request):
    """用户权限管理使用指南页面"""
    return render(request, 'admin/user_permission_guide.html')


@login_required
@system_settings_required
def simple_user_permissions_page(request):
    """简化版用户权限管理页面"""
    
    try:
        from django.contrib.auth.models import User
        from home.models import Parameter
        from django.db.models import Q
        import json
        
        # 获取搜索参数
        search_query = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()
        
        # 构建用户查询
        users_query = User.objects.all()
        
        # 应用搜索过滤
        if search_query:
            users_query = users_query.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # 应用状态过滤
        if status_filter:
            if status_filter == 'active':
                users_query = users_query.filter(is_active=True)
            elif status_filter == 'inactive':
                users_query = users_query.filter(is_active=False)
        
        # 获取用户列表
        users = users_query.order_by('username')
        
        # 定义所有QC报表模块
        modules = [
            {'name': '东泰QC报表', 'code': 'dongtai_qc_report'},
            {'name': '大塬QC报表', 'code': 'dayuan_qc_report'},
            {'name': '长富QC报表', 'code': 'changfu_qc_report'},
            {'name': '远通QC报表', 'code': 'yuantong_qc_report'},
            {'name': '远通二线QC报表', 'code': 'yuantong2_qc_report'},
            {'name': '兴辉QC报表', 'code': 'xinghui_qc_report'},
            {'name': '兴辉二线QC报表', 'code': 'xinghui2_qc_report'}
        ]
        
        # 获取每个用户每个模块的权限配置
        user_permissions = {}
        for user in users:
            user_permissions[user.username] = {}
            for module in modules:
                user_permissions_id = f'{module["code"]}_permissions_{user.username}'
                param = Parameter.objects.filter(id=user_permissions_id).first()
                if param and param.value:
                    try:
                        user_permissions[user.username][module["code"]] = json.loads(param.value)
                    except:
                        user_permissions[user.username][module["code"]] = {
                            'view': False, 'edit': False, 'edit_others': False,
                            'delete': False, 'manage': False
                        }
                else:
                    user_permissions[user.username][module["code"]] = {
                        'view': False, 'edit': False, 'edit_others': False,
                        'delete': False, 'manage': False
                    }
        
        # 获取菜单数据
        from home.utils.permissions import filter_menu_by_permission
        filtered_menu_items = filter_menu_by_permission(MENU_ITEMS, request.user.username)
        
        context = {
            'users': users,
            'modules': modules,
            'user_permissions': user_permissions,
            'search_query': search_query,
            'status_filter': status_filter,
            'total_users': User.objects.count(),
            'filtered_users_count': users.count(),
            'menu_items': filtered_menu_items
        }
        
        return render(request, 'admin/simple_user_permissions.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': f'加载用户权限管理页面失败：{str(e)}'
        })

@login_required
def user_permission_management(request):
    """用户权限管理页面"""
    # 检查访问权限
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return HttpResponse('权限不足', status=403)
    
    # 获取所有用户
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('username')
    
    # 定义所有QC报表模块
    modules = [
        {'name': '东泰QC报表', 'code': 'dongtai_qc_report'},
        {'name': '大塬QC报表', 'code': 'dayuan_qc_report'},
        {'name': '长富QC报表', 'code': 'changfu_qc_report'},
        {'name': '远通QC报表', 'code': 'yuantong_qc_report'},
        {'name': '远通二线QC报表', 'code': 'yuantong2_qc_report'},
        {'name': '兴辉QC报表', 'code': 'xinghui_qc_report'},
        {'name': '兴辉二线QC报表', 'code': 'xinghui2_qc_report'}
    ]
    
    # 获取当前权限配置
    from home.models import Parameter
    import json
    
    user_permissions = {}
    for user in users:
        user_permissions[user.username] = {}
        for module in modules:
            user_permissions_id = f'{module["code"]}_permissions_{user.username}'
            param = Parameter.objects.filter(id=user_permissions_id).first()
            if param and param.value:
                try:
                    user_permissions[user.username][module["code"]] = json.loads(param.value)
                except:
                    user_permissions[user.username][module["code"]] = {
                        'view': False,
                        'edit': False,
                        'edit_others': False,
                        'delete': False,
                        'manage': False
                    }
            else:
                user_permissions[user.username][module["code"]] = {
                    'view': False,
                    'edit': False,
                    'edit_others': False,
                    'delete': False,
                    'manage': False
                }
    
    context = {
        'users': users,
        'modules': modules,
        'user_permissions': user_permissions
    }
    
    return render(request, 'admin/user_permission_management.html', context)

@login_required
@csrf_exempt
def update_user_permissions(request):
    """更新用户权限API"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '只支持POST请求'})
    
    # 检查访问权限
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return JsonResponse({'status': 'error', 'message': '权限不足'})
    
    try:
        import json
        from django.contrib.auth.models import User
        from home.models import Parameter
        
        # 获取请求数据
        data = json.loads(request.body)
        action = data.get('action')
        
        # 处理跨用户编辑快速设置
        if action == 'enable_cross_edit':
            # 启用跨用户编辑功能
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': 'true'}
            )
            # 为所有模块启用跨用户编辑权限
            modules = ['dongtai_qc_report', 'dayuan_qc_report', 'changfu_qc_report', 
                      'yuantong_qc_report', 'yuantong2_qc_report', 'xinghui_qc_report', 'xinghui2_qc_report']
            for module in modules:
                permissions = {
                    'view': True,
                    'edit': True,
                    'edit_others': True,
                    'delete': True,
                    'manage': True
                }
                Parameter.objects.update_or_create(
                    id=f'{module}_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
            return JsonResponse({'status': 'success', 'message': '跨用户编辑功能已启用'})
            
        elif action == 'disable_cross_edit':
            # 禁用跨用户编辑功能
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': 'false'}
            )
            return JsonResponse({'status': 'success', 'message': '跨用户编辑功能已禁用'})
        
        # 处理用户权限设置
        username = data.get('username')
        module_code = data.get('module_code', 'dongtai_qc_report')  # 默认东泰
        permissions = data.get('permissions', {})
        
        if not username:
            return JsonResponse({'status': 'error', 'message': '用户名不能为空'})
        
        if not module_code:
            return JsonResponse({'status': 'error', 'message': '模块代码不能为空'})
        
        # 验证用户是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'})
        
        # 保存权限配置
        user_permissions_id = f'{module_code}_permissions_{username}'
        Parameter.objects.update_or_create(
            id=user_permissions_id,
            defaults={'value': json.dumps(permissions)}
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'用户 {username} 的权限已更新',
            'permissions': permissions
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON格式错误'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'更新失败：{str(e)}'})

@login_required
def get_user_permissions(request):
    """获取用户权限API"""
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': '只支持GET请求'})
    
    # 检查访问权限
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return JsonResponse({'status': 'error', 'message': '权限不足'})
    
    try:
        import json
        from django.contrib.auth.models import User
        from home.models import Parameter
        
        # 检查是否是获取跨用户编辑状态
        if not request.GET.get('username'):
            # 返回跨用户编辑状态
            cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
            cross_edit_enabled = cross_edit_param and cross_edit_param.value == 'true'
            
            return JsonResponse({
                'status': 'success',
                'cross_edit_enabled': cross_edit_enabled
            })
        
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'status': 'error', 'message': '用户名不能为空'})
        
        # 验证用户是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'})
        
        # 获取权限配置
        user_permissions_id = f'dongtai_qc_report_permissions_{username}'
        param = Parameter.objects.filter(id=user_permissions_id).first()
        
        if param and param.value:
            try:
                permissions = json.loads(param.value)
            except:
                permissions = {
                    'view': False,
                    'edit': False,
                    'edit_others': False,
                    'delete': False,
                    'manage': False
                }
        else:
            permissions = {
                'view': False,
                'edit': False,
                'edit_others': False,
                'delete': False,
                'manage': False
            }
        
        return JsonResponse({
            'status': 'success',
            'permissions': permissions
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取失败：{str(e)}'})



@login_required
@csrf_exempt
@permission_required('qc_report_edit')
# QC报表相关代码已移动到 home/views/qc_reports.py
@login_required
def changfu_debug_simple(request):
    """长富QC报表简单调试页面"""
    return render(request, 'production/changfu_debug_simple.html')






def admin_permission_settings(request):
    """权限设置管理页面"""
    # 允许超级管理员和指定的管理员用户访问
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return render(request, 'error.html', {
            'error_message': '只有超级管理员或指定管理员才能访问权限设置页面',
            'back_url': '/'
        })
    
    if request.method == 'POST':
        try:
            # 处理权限设置保存
            from home.models import Parameter
            import json
            
            # 保存基础设置
            cross_user_edit = request.POST.get('enable_cross_user_edit', 'false')
            edit_limit = request.POST.get('report_edit_limit', '7')
            
            # 更新或创建参数
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': cross_user_edit}
            )
            Parameter.objects.update_or_create(
                id='report_edit_limit',
                defaults={'value': edit_limit}
            )
            
            # 保存模块权限设置
            modules = [
                'yuantong_qc_report', 'dayuan_qc_report', 'dongtai_qc_report',
                'xinghui_qc_report', 'changfu_qc_report', 'yuantong2_qc_report',
                'xinghui2_qc_report'
            ]
            
            for module in modules:
                permissions = {
                    'view': request.POST.get(f'{module}_view') == 'on',
                    'edit': request.POST.get(f'{module}_edit') == 'on',
                    'edit_others': request.POST.get(f'{module}_edit_others') == 'on',
                    'delete': request.POST.get(f'{module}_delete') == 'on',
                    'manage': request.POST.get(f'{module}_manage') == 'on'
                }
                
                Parameter.objects.update_or_create(
                    id=f'{module}_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
            
            # 保存角色权限设置
            available_roles = [
                'qc_manager', 'production_manager', 'quality_supervisor',
                'department_head', 'admin'
            ]
            
            cross_edit_roles = []
            for role in available_roles:
                if request.POST.get(f'cross_edit_role_{role}') == 'on':
                    cross_edit_roles.append(role)
            
            Parameter.objects.update_or_create(
                id='cross_edit_roles',
                defaults={'value': json.dumps(cross_edit_roles)}
            )
            
            return JsonResponse({'status': 'success', 'message': '权限设置保存成功'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'保存失败：{str(e)}'})
    
    # GET请求 - 显示设置页面
    try:
        from home.models import Parameter
        import json
        
        # 获取当前设置
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        cross_user_edit_enabled = cross_edit_param and cross_edit_param.value == 'true'
        
        edit_limit_param = Parameter.objects.filter(id='report_edit_limit').first()
        edit_limit = int(edit_limit_param.value) if edit_limit_param and edit_limit_param.value else 7
        
        # 获取模块权限设置
        modules = [
            {'name': '远通QC报表', 'code': 'yuantong_qc_report'},
            {'name': '大塬QC报表', 'code': 'dayuan_qc_report'},
            {'name': '东泰QC报表', 'code': 'dongtai_qc_report'},
            {'name': '兴辉QC报表', 'code': 'xinghui_qc_report'},
            {'name': '长富QC报表', 'code': 'changfu_qc_report'},
            {'name': '远通二线QC报表', 'code': 'yuantong2_qc_report'},
            {'name': '兴辉二线QC报表', 'code': 'xinghui2_qc_report'}
        ]
        
        for module in modules:
            param = Parameter.objects.filter(id=f'{module["code"]}_permissions').first()
            if param and param.value:
                module['permissions'] = json.loads(param.value)
            else:
                module['permissions'] = {
                    'view': False, 'edit': False, 'edit_others': False,
                    'delete': False, 'manage': False
                }
        
        # 获取角色权限设置
        roles_param = Parameter.objects.filter(id='cross_edit_roles').first()
        cross_edit_roles = []
        if roles_param and roles_param.value:
            cross_edit_roles = json.loads(roles_param.value)
        
        available_roles = [
            {'name': 'QC经理', 'code': 'qc_manager'},
            {'name': '生产经理', 'code': 'production_manager'},
            {'name': '质量主管', 'code': 'quality_supervisor'},
            {'name': '部门主管', 'code': 'department_head'},
            {'name': '系统管理员', 'code': 'admin'}
        ]
        
        for role in available_roles:
            role['can_cross_edit'] = role['code'] in cross_edit_roles
        
        context = {
            'cross_user_edit_enabled': cross_user_edit_enabled,
            'edit_limit': edit_limit,
            'modules': modules,
            'available_roles': available_roles
        }
        
        return render(request, 'admin/permission_settings.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': f'加载权限设置页面失败：{str(e)}'
        })


def simple_permission_config(request):
    """简单权限配置页面 - 不需要特殊权限"""
    if request.method == 'POST':
        try:
            from home.models import Parameter
            import json
            
            action = request.POST.get('action')
            
            if action == 'enable_all':
                # 启用跨用户编辑功能
                Parameter.objects.update_or_create(
                    id='enable_cross_user_edit',
                    defaults={'value': 'true'}
                )
                # 为东泰QC报表启用跨用户编辑权限
                permissions = {
                    'view': True,
                    'edit': True,
                    'edit_others': True,
                    'delete': True,
                    'manage': True
                }
                Parameter.objects.update_or_create(
                    id='dongtai_qc_report_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
                return JsonResponse({'status': 'success', 'message': '已启用跨用户编辑功能'})
                
            elif action == 'disable_all':
                # 禁用跨用户编辑功能
                Parameter.objects.update_or_create(
                    id='enable_cross_user_edit',
                    defaults={'value': 'false'}
                )
                return JsonResponse({'status': 'success', 'message': '已禁用跨用户编辑功能'})
                
            elif action == 'update_limit':
                # 更新编辑期限
                edit_limit = request.POST.get('edit_limit', '7')
                Parameter.objects.update_or_create(
                    id='report_edit_limit',
                    defaults={'value': edit_limit}
                )
                return JsonResponse({'status': 'success', 'message': f'已更新编辑期限为 {edit_limit} 天'})
                
            elif action == 'save_detail':
                # 保存详细配置
                cross_user_edit = request.POST.get('enable_cross_user_edit') == 'true'
                dongtai_edit_others = request.POST.get('dongtai_edit_others') == 'true'
                
                Parameter.objects.update_or_create(
                    id='enable_cross_user_edit',
                    defaults={'value': 'true' if cross_user_edit else 'false'}
                )
                
                permissions = {
                    'view': True,
                    'edit': True,
                    'edit_others': dongtai_edit_others,
                    'delete': True,
                    'manage': True
                }
                Parameter.objects.update_or_create(
                    id='dongtai_qc_report_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
                
                return JsonResponse({'status': 'success', 'message': '详细配置已保存'})
            else:
                # 如果没有匹配到任何action，返回错误
                return JsonResponse({'status': 'error', 'message': '无效的操作类型'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'保存失败：{str(e)}'})
    
    # GET请求 - 显示配置页面
    try:
        from home.models import Parameter
        import json
        
        # 获取当前设置
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        cross_user_edit_enabled = cross_edit_param and cross_edit_param.value == 'true'
        
        edit_limit_param = Parameter.objects.filter(id='report_edit_limit').first()
        edit_limit = int(edit_limit_param.value) if edit_limit_param and edit_limit_param.value else 7
        
        # 获取东泰QC报表权限设置
        dongtai_param = Parameter.objects.filter(id='dongtai_qc_report_permissions').first()
        dongtai_edit_others = False
        if dongtai_param and dongtai_param.value:
            try:
                permissions = json.loads(dongtai_param.value)
                dongtai_edit_others = permissions.get('edit_others', False)
            except:
                pass
        
        context = {
            'cross_user_edit_enabled': cross_user_edit_enabled,
            'edit_limit': edit_limit,
            'dongtai_edit_others': dongtai_edit_others
        }
        
        return render(request, 'admin/simple_permission_config.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': f'加载权限配置页面失败：{str(e)}'
        })



def debug_user_permissions_page(request):
    """调试用户权限管理页面"""
    return render(request, 'admin/debug_user_permissions.html')


def user_permission_guide_page(request):
    """用户权限管理使用指南页面"""
    return render(request, 'admin/user_permission_guide.html')



def simple_user_permissions_page(request):
    """简化版用户权限管理页面"""
    
    try:
        from django.contrib.auth.models import User
        from home.models import Parameter
        from django.db.models import Q
        import json
        
        # 获取搜索参数
        search_query = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()
        
        # 构建用户查询
        users_query = User.objects.all()
        
        # 应用搜索过滤
        if search_query:
            users_query = users_query.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # 应用状态过滤
        if status_filter:
            if status_filter == 'active':
                users_query = users_query.filter(is_active=True)
            elif status_filter == 'inactive':
                users_query = users_query.filter(is_active=False)
        
        # 获取用户列表
        users = users_query.order_by('username')
        
        # 定义所有QC报表模块
        modules = [
            {'name': '东泰QC报表', 'code': 'dongtai_qc_report'},
            {'name': '大塬QC报表', 'code': 'dayuan_qc_report'},
            {'name': '长富QC报表', 'code': 'changfu_qc_report'},
            {'name': '远通QC报表', 'code': 'yuantong_qc_report'},
            {'name': '远通二线QC报表', 'code': 'yuantong2_qc_report'},
            {'name': '兴辉QC报表', 'code': 'xinghui_qc_report'},
            {'name': '兴辉二线QC报表', 'code': 'xinghui2_qc_report'}
        ]
        
        # 获取每个用户每个模块的权限配置
        user_permissions = {}
        for user in users:
            user_permissions[user.username] = {}
            for module in modules:
                user_permissions_id = f'{module["code"]}_permissions_{user.username}'
                param = Parameter.objects.filter(id=user_permissions_id).first()
                if param and param.value:
                    try:
                        user_permissions[user.username][module["code"]] = json.loads(param.value)
                    except:
                        user_permissions[user.username][module["code"]] = {
                            'view': False, 'edit': False, 'edit_others': False,
                            'delete': False, 'manage': False
                        }
                else:
                    user_permissions[user.username][module["code"]] = {
                        'view': False, 'edit': False, 'edit_others': False,
                        'delete': False, 'manage': False
                    }
        
        # 获取菜单数据
        from home.utils.permissions import filter_menu_by_permission
        filtered_menu_items = filter_menu_by_permission(MENU_ITEMS, request.user.username)
        
        context = {
            'users': users,
            'modules': modules,
            'user_permissions': user_permissions,
            'search_query': search_query,
            'status_filter': status_filter,
            'total_users': User.objects.count(),
            'filtered_users_count': users.count(),
            'menu_items': filtered_menu_items
        }
        
        return render(request, 'admin/simple_user_permissions.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': f'加载用户权限管理页面失败：{str(e)}'
        })


def user_permission_management(request):
    """用户权限管理页面"""
    # 检查访问权限
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return HttpResponse('权限不足', status=403)
    
    # 获取所有用户
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('username')
    
    # 定义所有QC报表模块
    modules = [
        {'name': '东泰QC报表', 'code': 'dongtai_qc_report'},
        {'name': '大塬QC报表', 'code': 'dayuan_qc_report'},
        {'name': '长富QC报表', 'code': 'changfu_qc_report'},
        {'name': '远通QC报表', 'code': 'yuantong_qc_report'},
        {'name': '远通二线QC报表', 'code': 'yuantong2_qc_report'},
        {'name': '兴辉QC报表', 'code': 'xinghui_qc_report'},
        {'name': '兴辉二线QC报表', 'code': 'xinghui2_qc_report'}
    ]
    
    # 获取当前权限配置
    from home.models import Parameter
    import json
    
    user_permissions = {}
    for user in users:
        user_permissions[user.username] = {}
        for module in modules:
            user_permissions_id = f'{module["code"]}_permissions_{user.username}'
            param = Parameter.objects.filter(id=user_permissions_id).first()
            if param and param.value:
                try:
                    user_permissions[user.username][module["code"]] = json.loads(param.value)
                except:
                    user_permissions[user.username][module["code"]] = {
                        'view': False,
                        'edit': False,
                        'edit_others': False,
                        'delete': False,
                        'manage': False
                    }
            else:
                user_permissions[user.username][module["code"]] = {
                    'view': False,
                    'edit': False,
                    'edit_others': False,
                    'delete': False,
                    'manage': False
                }
    
    context = {
        'users': users,
        'modules': modules,
        'user_permissions': user_permissions
    }
    
    return render(request, 'admin/user_permission_management.html', context)


def update_user_permissions(request):
    """更新用户权限API"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '只支持POST请求'})
    
    # 检查访问权限
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return JsonResponse({'status': 'error', 'message': '权限不足'})
    
    try:
        import json
        from django.contrib.auth.models import User
        from home.models import Parameter
        
        # 获取请求数据
        data = json.loads(request.body)
        action = data.get('action')
        
        # 处理跨用户编辑快速设置
        if action == 'enable_cross_edit':
            # 启用跨用户编辑功能
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': 'true'}
            )
            # 为所有模块启用跨用户编辑权限
            modules = ['dongtai_qc_report', 'dayuan_qc_report', 'changfu_qc_report', 
                      'yuantong_qc_report', 'yuantong2_qc_report', 'xinghui_qc_report', 'xinghui2_qc_report']
            for module in modules:
                permissions = {
                    'view': True,
                    'edit': True,
                    'edit_others': True,
                    'delete': True,
                    'manage': True
                }
                Parameter.objects.update_or_create(
                    id=f'{module}_permissions',
                    defaults={'value': json.dumps(permissions)}
                )
            return JsonResponse({'status': 'success', 'message': '跨用户编辑功能已启用'})
            
        elif action == 'disable_cross_edit':
            # 禁用跨用户编辑功能
            Parameter.objects.update_or_create(
                id='enable_cross_user_edit',
                defaults={'value': 'false'}
            )
            return JsonResponse({'status': 'success', 'message': '跨用户编辑功能已禁用'})
        
        # 处理用户权限设置
        username = data.get('username')
        module_code = data.get('module_code', 'dongtai_qc_report')  # 默认东泰
        permissions = data.get('permissions', {})
        
        if not username:
            return JsonResponse({'status': 'error', 'message': '用户名不能为空'})
        
        if not module_code:
            return JsonResponse({'status': 'error', 'message': '模块代码不能为空'})
        
        # 验证用户是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'})
        
        # 保存权限配置
        user_permissions_id = f'{module_code}_permissions_{username}'
        Parameter.objects.update_or_create(
            id=user_permissions_id,
            defaults={'value': json.dumps(permissions)}
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'用户 {username} 的权限已更新',
            'permissions': permissions
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON格式错误'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'更新失败：{str(e)}'})


def get_user_permissions(request):
    """获取用户权限API"""
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': '只支持GET请求'})
    
    # 检查访问权限
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if not request.user.is_superuser and request.user.username not in admin_users:
        return JsonResponse({'status': 'error', 'message': '权限不足'})
    
    try:
        import json
        from django.contrib.auth.models import User
        from home.models import Parameter
        
        # 检查是否是获取跨用户编辑状态
        if not request.GET.get('username'):
            # 返回跨用户编辑状态
            cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
            cross_edit_enabled = cross_edit_param and cross_edit_param.value == 'true'
            
            return JsonResponse({
                'status': 'success',
                'cross_edit_enabled': cross_edit_enabled
            })
        
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'status': 'error', 'message': '用户名不能为空'})
        
        # 验证用户是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'})
        
        # 获取权限配置
        user_permissions_id = f'dongtai_qc_report_permissions_{username}'
        param = Parameter.objects.filter(id=user_permissions_id).first()
        
        if param and param.value:
            try:
                permissions = json.loads(param.value)
            except:
                permissions = {
                    'view': False,
                    'edit': False,
                    'edit_others': False,
                    'delete': False,
                    'manage': False
                }
        else:
            permissions = {
                'view': False,
                'edit': False,
                'edit_others': False,
                'delete': False,
                'manage': False
            }
        
        return JsonResponse({
            'status': 'success',
            'permissions': permissions
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取失败：{str(e)}'})



@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
# QC报表相关代码已移动到 home/views/qc_reports.py
@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class UserPasswordResetAPI(View):
    """用户密码重置API"""

    def post(self, request, user_id):
        """重置用户密码"""
        try:
            data = json.loads(request.body)
            new_password = data.get('password')
            
            if not new_password:
                return JsonResponse({'status': 'error', 'message': '新密码不能为空'}, status=400)

            user = User.objects.get(id=user_id)
            
            # 更新Django用户密码
            user.set_password(new_password)
            user.save()
            
            # 更新UserProfile中的加密密码
            try:
                profile = user.profile  # 使用home.models.UserProfile
                encrypted_password = hashlib.sha256(new_password.encode()).hexdigest()
                profile.encrypted_password = encrypted_password
                profile.save()
            except Exception:
                # 如果UserProfile不存在，创建一个
                from home.models import UserProfile
                encrypted_password = hashlib.sha256(new_password.encode()).hexdigest()
                UserProfile.objects.create(
                    user=user,
                    encrypted_password=encrypted_password
                )

            return JsonResponse({
                'status': 'success',
                'message': '密码重置成功'
            })
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error resetting password: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@system_settings_required
def user_management(request):
    """用户管理页面"""
    # 用户管理页面被访问，当前用户: request.user.username
    return render(request, 'system/user_management.html', {
        'user': request.user,
        'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
    })


# 添加一个简单的测试视图

# 添加调试视图

@login_required
@csrf_exempt
def qc_test_report_page(request):
    """QC 功能测试报告网页：运行测试并展示报告（仅 staff 可访问）。POST 豁免 CSRF 以便表单提交。"""
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied('仅管理员可查看测试报告')
    run_requested = request.method == 'POST' or request.GET.get('run') == '1'
    report_records = []
    run_error = None
    if run_requested:
        from django.test import Client
        from test.test_all_qc_reports_e2e import run_qc_functional_test_for_web
        client = Client()
        client.force_login(request.user)
        host = request.get_host()
        report_records, run_error = run_qc_functional_test_for_web(client, host=host)
    total = len(report_records)
    summary = {}
    if report_records:
        summary = {
            'template_ok': sum(1 for r in report_records if r.get('template_ok')),
            'import_ok': sum(1 for r in report_records if r.get('import_ok')),
            'new_data_ok': sum(1 for r in report_records if r.get('new_data_ok')),
            'total': total,
        }
    return render(request, 'test/qc_test_report.html', {
        'report_records': report_records,
        'summary': summary,
        'run_error': run_error,
        'run_requested': run_requested,
    })


@login_required
def debug_user_info(request):
    """调试用户信息"""
    user_info = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'is_active': request.user.is_active,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'has_system_settings_permission': has_system_settings_permission(request.user.username),
        'is_admin_user': is_admin_user(request.user.username)
    }
    
    from django.http import JsonResponse
    return JsonResponse(user_info)


@method_decorator(csrf_exempt, name='dispatch')

class UserManagementAPI(View):
    """用户管理API视图"""

    def get(self, request, user_id=None):
        """获取用户列表或单个用户"""
        # UserManagementAPI.get called - user_id: user_id
        # Request user: request.user.username
        # Request user is authenticated: request.user.is_authenticated
        
        try:
            if user_id:
                # 获取单个用户
                # Getting single user with ID: user_id
                user = User.objects.get(id=user_id)
                profile = getattr(user, 'system_profile', None)
                data = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone': profile.phone if profile else '',
                    'wechat_id': profile.wechat_id if profile else '',
                    'employee_id': profile.employee_id if profile else '',
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
                }
                # Returning user data: data
                return JsonResponse({'status': 'success', 'data': data})
            else:
                # 获取用户列表（支持搜索和分页）
                # Getting user list with search and pagination
                
                # 获取查询参数
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                username = request.GET.get('username', '').strip()
                name = request.GET.get('name', '').strip()
                email = request.GET.get('email', '').strip()
                is_active = request.GET.get('is_active', '').strip()
                
                # 构建查询集
                queryset = User.objects.all()
                
                # 应用搜索过滤
                if username:
                    queryset = queryset.filter(username__icontains=username)
                
                if name:
                    queryset = queryset.filter(
                        Q(first_name__icontains=name) | 
                        Q(last_name__icontains=name) |
                        Q(first_name__icontains=name.split()[0]) |
                        Q(last_name__icontains=name.split()[-1] if len(name.split()) > 1 else name)
                    )
                
                if email:
                    queryset = queryset.filter(email__icontains=email)
                
                if is_active:
                    queryset = queryset.filter(is_active=is_active.lower() == 'true')
                
                # 排序
                queryset = queryset.order_by('-date_joined')
                
                # 计算总数
                total_count = queryset.count()
                
                # 分页
                start = (page - 1) * page_size
                end = start + page_size
                users = queryset[start:end]
                
                # 构建响应数据
                data = []
                for user in users:
                    profile = getattr(user, 'system_profile', None)
                    data.append({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or '',
                        'email': user.email or '',
                        'phone': profile.phone if profile else '',
                        'wechat_id': profile.wechat_id if profile else '',
                        'employee_id': profile.employee_id if profile else '',
                        'is_active': user.is_active,
                        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
                    })
                
                # 返回分页数据
                response_data = {
                    'results': data,
                    'count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
                
                # Returning len(data) users out of total_count total
                return JsonResponse({'status': 'success', 'data': response_data})
        except User.DoesNotExist:
            # User not found: user_id
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except Exception as e:
            # Error in UserManagementAPI.get: str(e)
            logger.error(f'Error getting user: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建新用户"""
        try:
            data = json.loads(request.body)
            username = data.get('username')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            wechat_id = data.get('wechat_id', '')
            employee_id = data.get('employee_id', '')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'status': 'error', 'message': '用户名和密码不能为空'}, status=400)

            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': '用户名已存在'}, status=400)

            # 创建用户
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # 生成加密密码用于用户名密码登录验证
            encrypted_password = hashlib.sha256(password.encode()).hexdigest()

            # 创建用户扩展信息
            from system.models import UserProfile as SystemUserProfile
            profile = SystemUserProfile.objects.create(
                user=user,
                phone=phone,
                wechat_id=wechat_id,
                employee_id=employee_id
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '用户创建成功',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': phone,
                    'wechat_id': wechat_id,
                    'employee_id': employee_id,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error creating user: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, user_id):
        """更新用户信息"""
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=user_id)
            from system.models import UserProfile as SystemUserProfile
            profile, created = SystemUserProfile.objects.get_or_create(user=user)

            # 更新用户基本信息
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            if 'is_active' in data:
                user.is_active = data['is_active']
            user.save()

            # 更新用户扩展信息
            if 'phone' in data:
                profile.phone = data['phone']
            if 'wechat_id' in data:
                profile.wechat_id = data['wechat_id']
            if 'employee_id' in data:
                profile.employee_id = data['employee_id']
            
            # 处理密码更新
            if 'password' in data and data['password']:
                # 更新Django用户密码
                user.set_password(data['password'])
                user.save()
                
                # 更新UserProfile中的加密密码
                try:
                    home_profile = user.profile  # 使用home.models.UserProfile
                    encrypted_password = hashlib.sha256(data['password'].encode()).hexdigest()
                    home_profile.encrypted_password = encrypted_password
                    home_profile.save()
                except Exception:
                    # 如果UserProfile不存在，创建一个
                    from home.models import UserProfile
                    encrypted_password = hashlib.sha256(data['password'].encode()).hexdigest()
                    UserProfile.objects.create(
                        user=user,
                        encrypted_password=encrypted_password
                    )
            
            profile.save()

            return JsonResponse({
                'status': 'success',
                'message': '用户更新成功',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': profile.phone,
                    'wechat_id': profile.wechat_id,
                    'employee_id': profile.employee_id,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
                }
            })
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error updating user: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, user_id):
        """删除用户"""
        try:
            user = User.objects.get(id=user_id)
            
            # 不能删除自己
            if user == request.user:
                return JsonResponse({'status': 'error', 'message': '不能删除当前登录用户'}, status=400)
            
            user.delete()
            return JsonResponse({'status': 'success', 'message': '用户删除成功'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error deleting user: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



class UserPasswordResetAPI(View):
    """用户密码重置API"""

    def post(self, request, user_id):
        """重置用户密码"""
        try:
            data = json.loads(request.body)
            new_password = data.get('password')
            
            if not new_password:
                return JsonResponse({'status': 'error', 'message': '新密码不能为空'}, status=400)

            user = User.objects.get(id=user_id)
            
            # 更新Django用户密码
            user.set_password(new_password)
            user.save()
            
            # 更新UserProfile中的加密密码
            try:
                profile = user.profile  # 使用home.models.UserProfile
                encrypted_password = hashlib.sha256(new_password.encode()).hexdigest()
                profile.encrypted_password = encrypted_password
                profile.save()
            except Exception:
                # 如果UserProfile不存在，创建一个
                from home.models import UserProfile
                encrypted_password = hashlib.sha256(new_password.encode()).hexdigest()
                UserProfile.objects.create(
                    user=user,
                    encrypted_password=encrypted_password
                )

            return JsonResponse({
                'status': 'success',
                'message': '密码重置成功'
            })
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error resetting password: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordLoginAPI(View):
    """用户名密码登录API"""
    
    def post(self, request):
        """处理用户名密码登录"""
        try:
            data = json.loads(request.body)
            username = data.get('username')
            hashed_password = data.get('password')  # 前端传来的加密密码
            salt = data.get('salt')  # 前端传来的盐值
            
            if not username or not hashed_password or not salt:
                return JsonResponse({
                    'status': 'error',
                    'message': '用户名、密码和盐值不能为空'
                }, status=400)
            
            # 查找用户
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': '用户名不存在'
                }, status=400)
            
            # 检查用户是否激活
            if not user.is_active:
                return JsonResponse({
                    'status': 'error',
                    'message': '用户账户已被禁用'
                }, status=400)
            
            # 验证加密密码
            if not self.verify_encrypted_password(user, hashed_password, salt):
                return JsonResponse({
                    'status': 'error',
                    'message': '密码错误'
                }, status=400)
            
            # 检查用户是否有密码（通过UserProfile中的wechat_id判断）
            try:
                profile = user.system_profile
                if not profile.wechat_id:
                    return JsonResponse({
                        'status': 'error',
                        'message': '该用户未设置企业微信ID，请使用扫码登录'
                    }, status=400)
            except SystemUserProfile.DoesNotExist:
                # 如果system_profile不存在，检查home.models.UserProfile
                try:
                    home_profile = user.profile
                    if not home_profile.wechat_id:
                        return JsonResponse({
                            'status': 'error',
                            'message': '该用户未设置企业微信ID，请使用扫码登录'
                        }, status=400)
                    profile = home_profile
                except UserProfile.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': '用户信息不完整，请联系管理员'
                    }, status=400)
            
            # 登录用户
            login(request, user)
            
            # 获取企业微信用户信息
            wechat_name = self.get_wechat_user_name(profile.wechat_id)
            
            return JsonResponse({
                'status': 'success',
                'message': '登录成功',
                'data': {
                    'username': user.username,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'wechat_name': wechat_name,
                    'wechat_id': profile.wechat_id
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '无效的请求数据'
            }, status=400)
        except Exception as e:
            import traceback
            logger.error(f'Password login error: {str(e)}\n{traceback.format_exc()}')
            # 返回具体错误便于排查（生产环境可改为仅返回通用提示）
            return JsonResponse({
                'status': 'error',
                'message': f'登录失败: {type(e).__name__}: {str(e)}'
            }, status=500)
    
    def verify_encrypted_password(self, user, hashed_password, salt):
        """验证加密密码"""
        try:
            import hashlib
            
            # 获取用户的扩展信息（从home.models.UserProfile）
            try:
                profile = user.profile
            except Exception:
                return False
            
            # 检查是否有存储的加密密码
            if not profile.encrypted_password:
                return False
            
            # 前端加密逻辑：
            # 1. 先对原始密码进行SHA-256哈希
            # 2. 然后对哈希值加盐再次哈希
            # 3. 发送最终的哈希值
            
            # 后端验证逻辑：
            # 1. 获取存储的原始密码哈希值
            stored_password_hash = profile.encrypted_password
            
            # 2. 对存储的哈希值加盐再次哈希
            salted_hash = hashlib.sha256((stored_password_hash + salt).encode()).hexdigest()
            
            # 3. 比较最终哈希值
            return hashed_password == salted_hash
            
        except Exception as e:
            logger.error(f'Password verification error: {str(e)}')
            return False
    
    def get_wechat_user_name(self, wechat_id):
        """根据企业微信ID获取用户名称"""
        try:
            # 获取企业微信配置
            corp_id = os.environ.get('WECHAT_CORP_ID')
            corp_secret = os.environ.get('WECHAT_CONTACT_SECRET')
            
            if not corp_id or not corp_secret:
                logger.warning('Missing WeChat configuration for getting user name')
                return wechat_id
            
            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}'
            token_resp = requests.get(token_url, timeout=5)
            token_data = token_resp.json()
            
            if token_data.get('errcode') != 0:
                logger.warning(f'Failed to get WeChat token: {token_data}')
                return wechat_id
            
            access_token = token_data.get('access_token')
            
            # 获取用户详细信息
            user_url = f'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={wechat_id}'
            user_resp = requests.get(user_url, timeout=5)
            user_data = user_resp.json()
            
            if user_data.get('errcode') == 0:
                return user_data.get('name', wechat_id)
            else:
                logger.warning(f'Failed to get WeChat user info: {user_data}')
                return wechat_id
                
        except Exception as e:
            logger.error(f'Error getting WeChat user name: {str(e)}')
            return wechat_id



# ==================== 产品型号API ====================

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class ProductModelAPI(View):
    """产品型号API"""
    
    def get(self, request, model_id=None):
        """获取产品型号列表或单个产品型号"""
        try:
            if model_id:
                # 获取单个产品型号
                product_model = ProductModel.objects.get(id=model_id)
                data = {
                    'id': product_model.id,
                    'name': product_model.name,
                    'created_at': product_model.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': product_model.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': data})
            else:
                # 获取产品型号列表
                product_models = ProductModel.objects.all().order_by('name')
                data = [{
                    'id': model.id,
                    'name': model.name,
                    'created_at': model.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': model.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                } for model in product_models]
                return JsonResponse({'status': 'success', 'data': data})
        except ProductModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '产品型号不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建新产品型号"""
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '产品型号名称不能为空'}, status=400)
            
            # 检查是否已存在同名产品型号
            if ProductModel.objects.filter(name=name).exists():
                return JsonResponse({'status': 'error', 'message': '产品型号名称已存在'}, status=400)
            
            product_model = ProductModel.objects.create(name=name)
            
            return JsonResponse({
                'status': 'success',
                'message': '创建成功',
                'data': {
                    'id': product_model.id,
                    'name': product_model.name
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, model_id):
        """更新产品型号"""
        try:
            product_model = ProductModel.objects.get(id=model_id)
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '产品型号名称不能为空'}, status=400)
            
            # 检查是否已存在同名产品型号（排除当前记录）
            if ProductModel.objects.filter(name=name).exclude(id=model_id).exists():
                return JsonResponse({'status': 'error', 'message': '产品型号名称已存在'}, status=400)
            
            product_model.name = name
            product_model.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '更新成功',
                'data': {
                    'id': product_model.id,
                    'name': product_model.name
                }
            })
        except ProductModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '产品型号不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, model_id):
        """删除产品型号"""
        try:
            product_model = ProductModel.objects.get(id=model_id)
            product_model.delete()
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except ProductModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '产品型号不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ==================== 包装类型API ====================

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class PackagingAPI(View):
    """包装类型API"""
    
    def get(self, request, packaging_id=None):
        """获取包装类型列表或单个包装类型"""
        try:
            if packaging_id:
                # 获取单个包装类型
                packaging = Packaging.objects.get(id=packaging_id)
                data = {
                    'id': packaging.id,
                    'name': packaging.name,
                    'created_at': packaging.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': packaging.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': data})
            else:
                # 获取包装类型列表
                packagings = Packaging.objects.all().order_by('name')
                data = [{
                    'id': packaging.id,
                    'name': packaging.name,
                    'created_at': packaging.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': packaging.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                } for packaging in packagings]
                return JsonResponse({'status': 'success', 'data': data})
        except Packaging.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '包装类型不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建新包装类型"""
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '包装类型名称不能为空'}, status=400)
            
            # 检查是否已存在同名包装类型
            if Packaging.objects.filter(name=name).exists():
                return JsonResponse({'status': 'error', 'message': '包装类型名称已存在'}, status=400)
            
            packaging = Packaging.objects.create(name=name)
            
            return JsonResponse({
                'status': 'success',
                'message': '创建成功',
                'data': {
                    'id': packaging.id,
                    'name': packaging.name
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, packaging_id):
        """更新包装类型"""
        try:
            packaging = Packaging.objects.get(id=packaging_id)
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '包装类型名称不能为空'}, status=400)
            
            # 检查是否已存在同名包装类型（排除当前记录）
            if Packaging.objects.filter(name=name).exclude(id=packaging_id).exists():
                return JsonResponse({'status': 'error', 'message': '包装类型名称已存在'}, status=400)
            
            packaging.name = name
            packaging.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '更新成功',
                'data': {
                    'id': packaging.id,
                    'name': packaging.name
                }
            })
        except Packaging.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '包装类型不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, packaging_id):
        """删除包装类型"""
        try:
            packaging = Packaging.objects.get(id=packaging_id)
            packaging.delete()
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except Packaging.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '包装类型不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ==================== 自动完成API ====================

@csrf_exempt
@login_required
def product_model_suggest(request):
    """产品型号自动完成API"""
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'status': 'success', 'data': []})
        
        # 搜索产品型号名称
        product_models = ProductModel.objects.filter(
            name__icontains=query
        ).order_by('name')[:10]  # 限制返回10个结果
        
        suggestions = [{
            'id': model.id,
            'name': model.name
        } for model in product_models]
        
        return JsonResponse({'status': 'success', 'data': suggestions})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'产品型号自动完成API错误: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def packaging_suggest(request):
    """包装类型自动完成API"""
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'status': 'success', 'data': []})
        
        # 搜索包装类型名称
        packagings = Packaging.objects.filter(
            name__icontains=query
        ).order_by('name')[:10]  # 限制返回10个结果
        
        suggestions = [{
            'id': packaging.id,
            'name': packaging.name
        } for packaging in packagings]
        
        return JsonResponse({'status': 'success', 'data': suggestions})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'包装类型自动完成API错误: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ==================== 用户收藏API ====================

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class UserFavoriteAPI(View):
    """用户收藏API"""
    
    def get(self, request):
        """获取用户收藏列表"""
        try:
            page = request.GET.get('page')
            
            if page == 'all':
                # 获取所有收藏，按页面分组返回
                user_favorites = UserFavorite.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                # 按页面分组
                favorites_by_page = {}
                for favorite in user_favorites:
                    page_key = favorite.favorite_id  # favorite_id存储的是页面标识
                    favorites_by_page[page_key] = {
                        'id': favorite.id,
                        'favorite_type': favorite.favorite_type,
                        'favorite_id': favorite.favorite_id,
                        'favorite_name': favorite.favorite_name,
                        'created_at': favorite.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                
                return JsonResponse({'status': 'success', 'data': favorites_by_page})
            
            elif page:
                # 检查特定页面是否已收藏
                favorite = UserFavorite.objects.filter(
                    user=request.user,
                    favorite_id=page
                ).first()
                
                if favorite:
                    return JsonResponse({
                        'status': 'success',
                        'favorite': {
                            'id': favorite.id,
                            'favorite_type': favorite.favorite_type,
                            'favorite_id': favorite.favorite_id,
                            'favorite_name': favorite.favorite_name,
                            'created_at': favorite.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    })
                else:
                    return JsonResponse({'status': 'success', 'favorite': None})
            
            else:
                # 返回所有收藏列表（兼容旧版本）
                user_favorites = UserFavorite.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                data = [{
                    'id': favorite.id,
                    'favorite_type': favorite.favorite_type,
                    'favorite_id': favorite.favorite_id,
                    'favorite_name': favorite.favorite_name,
                    'created_at': favorite.created_at.strftime('%Y-%m-%d %H:%M:%S')
                } for favorite in user_favorites]
                
                return JsonResponse({'status': 'success', 'data': data})
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'用户收藏API错误: {str(e)}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """添加用户收藏"""
        try:
            data = json.loads(request.body)
            page = data.get('page')
            
            if not page:
                return JsonResponse({'status': 'error', 'message': '缺少页面参数'}, status=400)
            
            # 根据页面类型设置收藏信息
            page_configs = {
                'dayuan_report': {
                    'favorite_type': 'page',
                    'favorite_name': '大塬QC报表'
                },
                'dongtai_report': {
                    'favorite_type': 'page',
                    'favorite_name': '东泰QC报表'
                },
                'changfu_report': {
                    'favorite_type': 'page',
                    'favorite_name': '长富QC报表'
                },
                'yauntong_report': {
                    'favorite_type': 'page',
                    'favorite_name': '远通QC报表'
                },
                'yuantong2_report': {
                    'favorite_type': 'page',
                    'favorite_name': '远通二线QC报表'
                },
                'xinghui_report': {
                    'favorite_type': 'page',
                    'favorite_name': '兴辉QC报表'
                },
                'xinghui2_report': {
                    'favorite_type': 'page',
                    'favorite_name': '兴辉二线QC报表'
                },
                'raw_soil_storage': {
                    'favorite_type': 'page',
                    'favorite_name': '原土入库'
                }
            }
            
            if page not in page_configs:
                return JsonResponse({'status': 'error', 'message': '不支持的页面类型'}, status=400)
            
            config = page_configs[page]
            
            # 检查是否已存在相同收藏
            if UserFavorite.objects.filter(
                user=request.user,
                favorite_id=page
            ).exists():
                return JsonResponse({'status': 'error', 'message': '已收藏此页面'}, status=400)
            
            favorite = UserFavorite.objects.create(
                user=request.user,
                favorite_type=config['favorite_type'],
                favorite_id=page,
                favorite_name=config['favorite_name']
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '收藏成功',
                'data': {
                    'id': favorite.id,
                    'favorite_type': favorite.favorite_type,
                    'favorite_id': favorite.favorite_id,
                    'favorite_name': favorite.favorite_name
                }
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'用户收藏API错误: {str(e)}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request):
        """删除用户收藏"""
        try:
            page = request.GET.get('page')
            
            if not page:
                return JsonResponse({'status': 'error', 'message': '缺少页面参数'}, status=400)
            
            favorite = UserFavorite.objects.get(
                favorite_id=page,
                user=request.user
            )
            favorite.delete()
            
            return JsonResponse({'status': 'success', 'message': '取消收藏成功'})
        except UserFavorite.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '收藏不存在'}, status=404)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'用户收藏API错误: {str(e)}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ==================== 包装类型管理页面 ====================

@login_required
@system_settings_required
def packaging(request):
    """包装类型管理页面"""
    return render(request, 'system/packaging.html', {
        'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
    })


# ==================== 产品型号管理页面 ====================

@login_required
@system_settings_required
def product_model(request):
    """产品型号管理页面"""
    return render(request, 'system/product_model.html', {
        'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
    })


# RBAC权限管理API
@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class RBACRoleAPI(View):
    """角色管理API"""
    
    def get(self, request, role_id=None):
        """获取角色列表或单个角色"""
        try:
            from system.models import Role
            from django.db.models import Q
            
            if role_id:
                # 获取单个角色
                role = Role.objects.get(id=role_id)
                role_data = {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': role.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': role_data})
            else:
                # 获取角色列表（支持搜索和分页）
                # 获取查询参数
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                role_name = request.GET.get('role_name', '').strip()
                description = request.GET.get('description', '').strip()
                
                # 构建查询集
                queryset = Role.objects.all()
                
                # 应用搜索过滤
                if role_name:
                    queryset = queryset.filter(name__icontains=role_name)
                
                if description:
                    queryset = queryset.filter(description__icontains=description)
                
                # 排序
                queryset = queryset.order_by('-created_at')
                
                # 计算总数
                total_count = queryset.count()
                
                # 分页
                start = (page - 1) * page_size
                end = start + page_size
                roles = queryset[start:end]
                
                # 构建响应数据
                roles_data = []
                for role in roles:
                    # 计算用户数量和权限数量
                    user_count = role.userrole_set.count()
                    permission_count = role.rolepermission_set.count()
                    
                    role_data = {
                        'id': role.id,
                        'name': role.name,
                        'description': role.description,
                        'user_count': user_count,
                        'permission_count': permission_count,
                        'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    roles_data.append(role_data)
                
                # 返回分页数据
                response_data = {
                    'results': roles_data,
                    'count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
                
                return JsonResponse({'status': 'success', 'data': response_data})
                
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACRoleAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建新角色"""
        try:
            from system.models import Role
            
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '角色名称不能为空'}, status=400)
            
            # 检查角色名是否已存在
            if Role.objects.filter(name=name).exists():
                return JsonResponse({'status': 'error', 'message': '角色名称已存在'}, status=400)
            
            role = Role.objects.create(name=name, description=description)
            
            return JsonResponse({
                'status': 'success',
                'message': '角色创建成功',
                'data': {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in RBACRoleAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, role_id):
        """更新角色"""
        try:
            from system.models import Role
            
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '角色名称不能为空'}, status=400)
            
            role = Role.objects.get(id=role_id)
            
            # 检查角色名是否已被其他角色使用
            if Role.objects.filter(name=name).exclude(id=role_id).exists():
                return JsonResponse({'status': 'error', 'message': '角色名称已存在'}, status=400)
            
            role.name = name
            role.description = description
            role.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '角色更新成功',
                'data': {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                }
            })
            
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in RBACRoleAPI.put: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, role_id):
        """删除角色"""
        try:
            from system.models import Role
            
            role = Role.objects.get(id=role_id)
            
            # 检查是否有用户使用此角色
            if role.userrole_set.exists():
                return JsonResponse({'status': 'error', 'message': '该角色下还有用户，无法删除'}, status=400)
            
            role.delete()
            
            return JsonResponse({'status': 'success', 'message': '角色删除成功'})
            
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACRoleAPI.delete: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, role_id=None):
        """获取角色列表或单个角色，或获取角色的权限"""
        try:
            from system.models import Role, RolePermission
            
            # 检查是否是获取角色权限的请求
            if role_id and 'permissions' in request.path:
                role = Role.objects.get(id=role_id)
                role_permissions = RolePermission.objects.filter(role=role).select_related('permission')
                
                permissions_data = []
                for role_perm in role_permissions:
                    permission_data = {
                        'id': role_perm.permission.id,
                        'code': role_perm.permission.code,
                        'name': role_perm.permission.name,
                        'description': role_perm.permission.description,
                        'permission_type': role_perm.permission.permission_type,
                        'module': role_perm.permission.module
                    }
                    permissions_data.append(permission_data)
                
                return JsonResponse({'status': 'success', 'data': permissions_data})
            
            # 原有的角色获取逻辑
            if role_id:
                # 获取单个角色
                role = Role.objects.get(id=role_id)
                role_data = {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': role.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': role_data})
            else:
                # 获取角色列表
                roles = Role.objects.all()
                roles_data = []
                for role in roles:
                    # 计算用户数量和权限数量
                    user_count = role.userrole_set.count()
                    permission_count = role.rolepermission_set.count()
                    
                    role_data = {
                        'id': role.id,
                        'name': role.name,
                        'description': role.description,
                        'user_count': user_count,
                        'permission_count': permission_count,
                        'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    roles_data.append(role_data)
                
                return JsonResponse({'status': 'success', 'data': roles_data})
                
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACRoleAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class RBACPermissionAPI(View):
    """权限管理API"""
    
    def get(self, request, permission_id=None):
        """获取权限列表或单个权限"""
        try:
            from system.models import Permission
            from django.db.models import Q
            
            if permission_id:
                # 获取单个权限
                permission = Permission.objects.get(id=permission_id)
                permission_data = {
                    'id': permission.id,
                    'code': permission.code,
                    'name': permission.name,
                    'description': permission.description,
                    'permission_type': permission.permission_type,
                    'module': permission.module,
                    'created_at': permission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': permission.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': permission_data})
            else:
                # 获取权限列表（支持搜索和分页）
                # 获取查询参数
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                permission_code = request.GET.get('permission_code', '').strip()
                permission_name = request.GET.get('permission_name', '').strip()
                permission_type = request.GET.get('permission_type', '').strip()
                module = request.GET.get('module', '').strip()
                
                # 构建查询集
                queryset = Permission.objects.all()
                
                # 应用搜索过滤
                if permission_code:
                    queryset = queryset.filter(code__icontains=permission_code)
                
                if permission_name:
                    queryset = queryset.filter(name__icontains=permission_name)
                
                if permission_type:
                    queryset = queryset.filter(permission_type=permission_type)
                
                if module:
                    queryset = queryset.filter(module__icontains=module)
                
                # 排序
                queryset = queryset.order_by('-created_at')
                
                # 计算总数
                total_count = queryset.count()
                
                # 分页
                start = (page - 1) * page_size
                end = start + page_size
                permissions = queryset[start:end]
                
                # 构建响应数据
                permissions_data = []
                for permission in permissions:
                    # 计算分配此权限的角色数量
                    role_count = permission.rolepermission_set.count()
                    
                    permission_data = {
                        'id': permission.id,
                        'code': permission.code,
                        'name': permission.name,
                        'description': permission.description,
                        'permission_type': permission.permission_type,
                        'module': permission.module,
                        'role_count': role_count,
                        'created_at': permission.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    permissions_data.append(permission_data)
                
                # 返回分页数据
                response_data = {
                    'results': permissions_data,
                    'count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
                
                return JsonResponse({'status': 'success', 'data': response_data})
                
        except Permission.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '权限不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACPermissionAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建新权限"""
        try:
            from system.models import Permission
            
            data = json.loads(request.body)
            code = data.get('code')
            name = data.get('name')
            permission_type = data.get('permission_type', 'operation')
            module = data.get('module', '')
            description = data.get('description', '')
            
            if not code or not name:
                return JsonResponse({'status': 'error', 'message': '权限代码和名称不能为空'}, status=400)
            
            # 检查权限代码是否已存在
            if Permission.objects.filter(code=code).exists():
                return JsonResponse({'status': 'error', 'message': '权限代码已存在'}, status=400)
            
            permission = Permission.objects.create(
                code=code,
                name=name,
                permission_type=permission_type,
                module=module,
                description=description
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '权限创建成功',
                'data': {
                    'id': permission.id,
                    'code': permission.code,
                    'name': permission.name,
                    'permission_type': permission.permission_type,
                    'module': permission.module,
                    'description': permission.description
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in RBACPermissionAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, permission_id):
        """更新权限"""
        try:
            data = json.loads(request.body)
            code = data.get('code')
            name = data.get('name')
            permission_type = data.get('permission_type', 'operation')
            module = data.get('module', '')
            description = data.get('description', '')
            
            if not code or not name:
                return JsonResponse({'status': 'error', 'message': '权限代码和名称不能为空'}, status=400)
            
            permission = Permission.objects.get(id=permission_id)
            
            # 检查权限代码是否已被其他权限使用
            if Permission.objects.filter(code=code).exclude(id=permission_id).exists():
                return JsonResponse({'status': 'error', 'message': '权限代码已存在'}, status=400)
            
            permission.code = code
            permission.name = name
            permission.permission_type = permission_type
            permission.module = module
            permission.description = description
            permission.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '权限更新成功',
                'data': {
                    'id': permission.id,
                    'code': permission.code,
                    'name': permission.name,
                    'permission_type': permission.permission_type,
                    'module': permission.module,
                    'description': permission.description
                }
            })
            
        except Permission.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '权限不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in RBACPermissionAPI.put: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, permission_id):
        """删除权限"""
        try:
            permission = Permission.objects.get(id=permission_id)
            
            # 检查是否有角色使用此权限
            if permission.rolepermission_set.exists():
                return JsonResponse({'status': 'error', 'message': '该权限下还有角色，无法删除'}, status=400)
            
            permission.delete()
            
            return JsonResponse({'status': 'success', 'message': '权限删除成功'})
            
        except Permission.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '权限不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACPermissionAPI.delete: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class RBACUserRoleAPI(View):
    """用户角色分配API"""
    
    def get(self, request, user_role_id=None):
        """获取用户角色分配列表或单个分配"""
        try:
            from system.models import UserRole
            from django.db.models import Q
            
            if user_role_id:
                # 获取单个用户角色分配
                user_role = UserRole.objects.get(id=user_role_id)
                user_role_data = {
                    'id': user_role.id,
                    'user': {
                        'id': user_role.user.id,
                        'username': user_role.user.username,
                        'first_name': user_role.user.first_name,
                        'last_name': user_role.user.last_name
                    },
                    'role': {
                        'id': user_role.role.id,
                        'name': user_role.role.name
                    },
                    'created_at': user_role.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return JsonResponse({'status': 'success', 'data': user_role_data})
            else:
                # 获取用户角色分配列表（支持搜索和分页）
                # 获取查询参数
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                username = request.GET.get('username', '').strip()
                name = request.GET.get('name', '').strip()
                role = request.GET.get('role', '').strip()
                
                # 构建查询集
                queryset = UserRole.objects.select_related('user', 'role').all()
                
                # 应用搜索过滤
                if username:
                    queryset = queryset.filter(user__username__icontains=username)
                
                if name:
                    queryset = queryset.filter(
                        Q(user__first_name__icontains=name) | 
                        Q(user__last_name__icontains=name)
                    )
                
                if role:
                    queryset = queryset.filter(role__name__icontains=role)
                
                # 排序
                queryset = queryset.order_by('-created_at')
                
                # 计算总数
                total_count = queryset.count()
                
                # 分页
                start = (page - 1) * page_size
                end = start + page_size
                user_roles = queryset[start:end]
                
                # 构建响应数据
                user_roles_data = []
                for user_role in user_roles:
                    user_role_data = {
                        'id': user_role.id,
                        'user': {
                            'id': user_role.user.id,
                            'username': user_role.user.username,
                            'first_name': user_role.user.first_name,
                            'last_name': user_role.user.last_name
                        },
                        'role': {
                            'id': user_role.role.id,
                            'name': user_role.role.name
                        },
                        'created_at': user_role.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    user_roles_data.append(user_role_data)
                
                # 返回分页数据
                response_data = {
                    'results': user_roles_data,
                    'count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
                
                return JsonResponse({'status': 'success', 'data': response_data})
                
        except UserRole.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户角色分配不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACUserRoleAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        """创建用户角色分配"""
        try:
            from system.models import Role, UserRole
            
            data = json.loads(request.body)
            user_id = data.get('user_id')
            role_id = data.get('role_id')
            
            if not user_id or not role_id:
                return JsonResponse({'status': 'error', 'message': '用户ID和角色ID不能为空'}, status=400)
            
            # 检查用户和角色是否存在
            try:
                user = User.objects.get(id=user_id)
                role = Role.objects.get(id=role_id)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
            except Role.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=400)
            
            # 检查是否已存在相同的用户角色分配
            if UserRole.objects.filter(user=user, role=role).exists():
                return JsonResponse({'status': 'error', 'message': '该用户已分配此角色'}, status=400)
            
            user_role = UserRole.objects.create(user=user, role=role)
            
            return JsonResponse({
                'status': 'success',
                'message': '用户角色分配成功',
                'data': {
                    'id': user_role.id,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name
                    },
                    'role': {
                        'id': role.id,
                        'name': role.name
                    }
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in RBACUserRoleAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, user_role_id):
        """删除用户角色分配"""
        try:
            from system.models import UserRole
            
            user_role = UserRole.objects.get(id=user_role_id)
            user_role.delete()
            
            return JsonResponse({'status': 'success', 'message': '用户角色分配删除成功'})
            
        except UserRole.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户角色分配不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACUserRoleAPI.delete: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@system_settings_required
def rbac_management(request):
    """RBAC权限管理页面"""
    return render(request, 'system/rbac_management.html', {
        'user': request.user,
        'menu_items': filter_menu_by_permission(MENU_ITEMS, request.user.username)
    })





def changfu_debug(request):
    """长富QC报表调试页面"""
    return render(request, 'production/changfu_debug.html')


def changfu_debug_simple(request):
    """长富QC报表简单调试页面"""
    return render(request, 'production/changfu_debug_simple.html')





@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class RBACRolePermissionAPI(View):
    """角色权限分配API"""
    
    def get(self, request, role_id):
        """获取角色的权限列表"""
        try:
            from system.models import Role, RolePermission
            
            role = Role.objects.get(id=role_id)
            role_permissions = RolePermission.objects.filter(role=role).select_related('permission')
            
            permissions_data = []
            for role_perm in role_permissions:
                permission_data = {
                    'id': role_perm.permission.id,
                    'code': role_perm.permission.code,
                    'name': role_perm.permission.name,
                    'description': role_perm.permission.description,
                    'permission_type': role_perm.permission.permission_type,
                    'module': role_perm.permission.module
                }
                permissions_data.append(permission_data)
            
            return JsonResponse({'status': 'success', 'data': permissions_data})
            
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in RBACRolePermissionAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request, role_id):
        """为角色分配权限"""
        try:
            from system.models import Role, Permission, RolePermission
            
            data = json.loads(request.body)
            permission_ids = data.get('permission_ids', [])
            
            role = Role.objects.get(id=role_id)
            
            # 清除现有权限分配
            RolePermission.objects.filter(role=role).delete()
            
            # 添加新的权限分配
            for permission_id in permission_ids:
                try:
                    permission = Permission.objects.get(id=permission_id)
                    RolePermission.objects.create(role=role, permission=permission)
                except Permission.DoesNotExist:
                    logger.warning(f'Permission {permission_id} does not exist')
                    continue
            
            return JsonResponse({'status': 'success', 'message': '角色权限分配成功'})
            
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '角色不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in RBACRolePermissionAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(system_settings_required, name='dispatch')
class PositionPermissionAPI(View):
    """职位权限分配API"""
    
    def get(self, request, position_id):
        """获取职位的权限列表"""
        try:
            from system.models import Position, PositionPermission
            
            position = Position.objects.get(id=position_id)
            position_permissions = PositionPermission.objects.filter(position=position).select_related('permission')
            
            permissions_data = []
            for pos_perm in position_permissions:
                permission_data = {
                    'id': pos_perm.permission.id,
                    'code': pos_perm.permission.code,
                    'name': pos_perm.permission.name,
                    'description': pos_perm.permission.description,
                    'permission_type': pos_perm.permission.permission_type,
                    'module': pos_perm.permission.module,
                    'is_inherited': pos_perm.is_inherited
                }
                permissions_data.append(permission_data)
            
            return JsonResponse({'status': 'success', 'data': permissions_data})
            
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '职位不存在'}, status=404)
        except Exception as e:
            logger.error(f'Error in PositionPermissionAPI.get: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request, position_id):
        """为职位分配权限"""
        try:
            from system.models import Position, Permission, PositionPermission
            
            data = json.loads(request.body)
            permission_ids = data.get('permission_ids', [])
            
            position = Position.objects.get(id=position_id)
            
            # 清除现有权限分配
            PositionPermission.objects.filter(position=position).delete()
            
            # 添加新的权限分配
            for permission_id in permission_ids:
                try:
                    permission = Permission.objects.get(id=permission_id)
                    PositionPermission.objects.create(position=position, permission=permission)
                except Permission.DoesNotExist:
                    logger.warning(f'Permission {permission_id} does not exist')
                    continue
            
            return JsonResponse({'status': 'success', 'message': '职位权限分配成功'})
            
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '职位不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            logger.error(f'Error in PositionPermissionAPI.post: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




def operation_log_view(request):
    """操作日志查询视图"""
    from django.shortcuts import render
    from django.core.paginator import Paginator
    from django.db.models import Q
    from django.db import models
    from .models import UserOperationLog
    
    # 检查用户权限
    if not user_has_permission(request.user, "qc_report_edit"):
        from django.shortcuts import render
        context = {
            "user": request.user,
            "request_path": request.path,
            "permission_code": "qc_report_edit"
        }
        return render(request, "403.html", context, status=403)
    
    # 获取查询参数
    username = request.GET.get("username", "")
    operation_type = request.GET.get("operation_type", "")
    report_type = request.GET.get("report_type", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    page = request.GET.get("page", 1)
    
    # 构建查询
    queryset = UserOperationLog.objects.all()
    
    if username:
        queryset = queryset.filter(username__icontains=username)
    
    if operation_type:
        queryset = queryset.filter(operation_type=operation_type)
    
    if report_type:
        queryset = queryset.filter(operation_type=operation_type)
    
    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)
    
    # 分页
    paginator = Paginator(queryset, 50)  # 每页50条记录
    try:
        logs = paginator.page(page)
    except:
        logs = paginator.page(1)
    
    # 获取统计信息
    total_logs = queryset.count()
    operation_type_stats = UserOperationLog.objects.values("operation_type").annotate(
        count=models.Count("id")
    ).order_by("-count")
    
    report_type_stats = UserOperationLog.objects.filter(
        report_type__isnull=False
    ).values("report_type").annotate(
        count=models.Count("id")
    ).order_by("-count")
    
    # 记录查看日志的操作
    UserOperationLog.log_operation(
        request=request,
        operation_type="VIEW",
        operation_detail=f"查看操作日志，筛选条件: 用户={username}, 操作类型={operation_type}, 报表类型={report_type}, 日期范围={start_date}~{end_date}"
    )
    
    # 根据用户权限过滤菜单 - 使用完整的菜单结构
    filtered_menu_items = filter_menu_by_permission(MENU_ITEMS, request.user.username)
    
    context = {
        "user": request.user,
        "menu_items": filtered_menu_items,
        "logs": logs,
        "total_logs": total_logs,
        "operation_type_stats": operation_type_stats,
        "report_type_stats": report_type_stats,
        "operation_types": UserOperationLog.OPERATION_TYPES,
        "report_types": UserOperationLog.REPORT_TYPES,
        "filters": {
            "username": username,
            "operation_type": operation_type,
            "report_type": report_type,
            "start_date": start_date,
            "end_date": end_date,
        }
    }
    
    return render(request, "system/operation_log.html", context)


def user_info_api(request):
    """获取当前用户信息API"""
    from django.http import JsonResponse
    
    if request.user.is_authenticated:
        return JsonResponse({
            "status": "success",
            "user": {
                "username": request.user.username,
                "is_superuser": request.user.is_superuser,
                "is_staff": request.user.is_staff,
                "email": request.user.email or "",
                "first_name": request.user.first_name or "",
                "last_name": request.user.last_name or "",
                "date_joined": request.user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if request.user.date_joined else "",
                "last_login": request.user.last_login.strftime("%Y-%m-%d %H:%M:%S") if request.user.last_login else ""
            }
        })
    else:
        return JsonResponse({
            "status": "error",
            "message": "用户未登录"
        }, status=401)

def operation_log_api(request):
    """操作日志API接口"""
    from django.http import JsonResponse
    from django.core.paginator import Paginator
    from .models import UserOperationLog
    
    # 检查用户权限
    if not user_has_permission(request.user, "qc_report_edit"):
        return JsonResponse({"status": "error", "message": "权限不足"}, status=403)
    
    try:
        # 获取查询参数
        username = request.GET.get("username", "")
        operation_type = request.GET.get("operation_type", "")
        report_type = request.GET.get("report_type", "")
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 50))
        
        # 构建查询
        queryset = UserOperationLog.objects.all()
        
        if username:
            queryset = queryset.filter(username__icontains=username)
        
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        if start_date:
            # 使用UTC时间进行查询，避免时区转换问题
            from django.utils import timezone
            import datetime
            start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            queryset = queryset.filter(created_at__gte=start_datetime)
        
        if end_date:
            # 使用UTC时间进行查询，避免时区转换问题
            from django.utils import timezone
            import datetime
            end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) + datetime.timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_datetime)
        
        # 分页
        paginator = Paginator(queryset, page_size)
        logs_page = paginator.page(page)
        
        # 序列化数据
        logs_data = []
        for log in logs_page:
            logs_data.append({
                "id": log.id,
                "username": log.username,
                "operation_type": log.operation_type,
                "operation_type_display": log.get_operation_type_display(),
                "report_type": log.report_type,
                "report_type_display": log.get_report_type_display() if log.report_type else "系统操作",
                "report_id": log.report_id,
                "operation_detail": log.operation_detail,
                "ip_address": log.ip_address,
                "request_path": log.request_path,
                "request_method": log.request_method,
                "created_at": log.created_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S"),
                "old_data": log.old_data,
                "new_data": log.new_data,
            })
        
        return JsonResponse({
            "status": "success",
            "data": {
                "logs": logs_data,
                "pagination": {
                    "current_page": page,
                    "total_pages": paginator.num_pages,
                    "total_count": paginator.count,
                    "has_previous": logs_page.has_previous(),
                    "has_next": logs_page.has_next(),
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"查询失败: {str(e)}"
        }, status=500)

@login_required
@csrf_exempt
def log_view_operation_api(request):
    """记录查看操作日志API"""
    from django.http import JsonResponse
    from .models import UserOperationLog
    import json
    import logging
    
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "仅支持POST请求"}, status=405)
    
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type')
        operation_type = data.get('operation_type', 'VIEW')
        operation_detail = data.get('operation_detail', '')
        request_path = data.get('request_path', request.path)
        debug_info = data.get('debug_info', {})
        
        # 记录详细的调试信息到Django日志
        logger = logging.getLogger('user_operations')
        logger.info(f"查看操作日志 - 用户: {request.user.username}, 报表类型: {report_type}, 客户端: {debug_info.get('clientInfo', {}).get('isWxWorkPC', False)}")
        
        if debug_info:
            logger.info(f"调试信息: {json.dumps(debug_info, ensure_ascii=False, indent=2)}")
        
        # 记录操作日志
        log_entry = UserOperationLog.log_operation(
            request=request,
            operation_type=operation_type,
            report_type=report_type,
            operation_detail=operation_detail
        )
        
        # 如果日志记录成功，记录更多调试信息
        if log_entry:
            logger.info(f"操作日志记录成功 - ID: {log_entry.id}")
            
            # 记录客户端环境信息
            client_info = debug_info.get('clientInfo', {})
            if client_info:
                logger.info(f"客户端环境: 企业微信={client_info.get('isWxWork', False)}, PC端={client_info.get('isWxWorkPC', False)}, 移动端={client_info.get('isMobile', False)}")
                logger.info(f"用户代理: {client_info.get('userAgent', '未知')}")
                logger.info(f"平台: {client_info.get('platform', '未知')}")
                logger.info(f"屏幕分辨率: {client_info.get('screenWidth', '未知')}x{client_info.get('screenHeight', '未知')}")
            
            # 记录页面状态信息
            page_state = debug_info.get('pageState', {})
            if page_state:
                logger.info(f"页面路径: {page_state.get('currentPath', '未知')}")
                logger.info(f"页面标题: {page_state.get('title', '未知')}")
                logger.info(f"访问时间: {page_state.get('timestamp', '未知')}")
            
            # 记录会话信息
            session_info = debug_info.get('sessionInfo', {})
            if session_info:
                logger.info(f"CSRF令牌: {session_info.get('hasCsrfToken', False)}")
                logger.info(f"会话Cookie: {session_info.get('hasSessionCookie', False)}")
                logger.info(f"Cookie长度: {session_info.get('sessionCookieLength', 0)}")
            
            # 记录页面元素状态
            element_state = debug_info.get('elementState', {})
            if element_state:
                logger.info(f"过滤表单: {element_state.get('hasFilterForm', False)}")
                logger.info(f"数据容器: {element_state.get('hasDataContainer', False)}")
                
                # 记录过滤表单元素详情
                filter_elements = element_state.get('filterFormElements', [])
                if filter_elements:
                    logger.info(f"过滤表单元素数量: {len(filter_elements)}")
                    for elem in filter_elements:
                        logger.info(f"  元素: {elem.get('name', '未知')} ({elem.get('type', '未知')}) = {elem.get('value', '空')}")
            
            # 记录错误信息（如果有）
            if 'error' in debug_info:
                logger.warning(f"操作过程中出现错误: {debug_info.get('error', '未知错误')}")
                if 'errorDetail' in debug_info:
                    logger.warning(f"错误详情: {debug_info.get('errorDetail', '')}")
                if 'errorStack' in debug_info:
                    logger.warning(f"错误堆栈: {debug_info.get('errorStack', '')}")
        
        return JsonResponse({
            "status": "success", 
            "message": "操作日志记录成功",
            "log_id": log_entry.id if log_entry else None,
            "debug_info_received": bool(debug_info)
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f'记录查看操作日志失败: {str(e)}', exc_info=True)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)





# export_qc_report_excel_universal 已移动到 home.utils.excel_export


# 微信认证相关代码已移动到 home/views/wechat_auth.py
