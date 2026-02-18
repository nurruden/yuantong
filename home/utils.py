from django.contrib.auth.models import User
from system.models import UserRole, RolePermission, Permission, Company, Department, Position, UserProfile, CompanyPermission, DepartmentPermission, PositionPermission
from home.config import get_report_permission_code

def has_data_permission(user, module, permission_type='view_all'):
    """
    检查用户是否有特定模块的数据权限
    
    Args:
        user: 用户对象
        module: 模块名称
        permission_type: 权限类型 ('view_own' 或 'view_all')
    
    Returns:
        bool: 是否有权限
    """
    if not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    # 获取用户的角色
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    
    for user_role in user_roles:
        # 检查角色是否有对应的权限
        permission_code = f"{module.lower().replace(' ', '_')}_{permission_type}"
        try:
            permission = Permission.objects.get(code=permission_code)
            if RolePermission.objects.filter(role=user_role.role, permission=permission).exists():
                return True
        except Permission.DoesNotExist:
            continue
    
    return False

def can_view_all_data(user, module):
    """
    检查用户是否可以查看指定模块的全部数据
    
    Args:
        user: 用户对象
        module: 模块名称
    
    Returns:
        bool: 是否可以查看全部数据
    """
    return has_data_permission(user, module, 'view_all')

def can_view_own_data(user, module):
    """
    检查用户是否可以查看指定模块的自己的数据
    
    Args:
        user: 用户对象
        module: 模块名称
    
    Returns:
        bool: 是否可以查看自己的数据
    """
    return has_data_permission(user, module, 'view_own')

def get_user_data_filter(user, module, user_field='created_by'):
    """
    根据用户权限获取数据过滤条件
    
    Args:
        user: 用户对象
        module: 模块名称
        user_field: 用户字段名（默认为'created_by'）
    
    Returns:
        dict: 过滤条件字典
    """
    if can_view_all_data(user, module):
        return {}  # 返回空字典表示不过滤
    elif can_view_own_data(user, module):
        return {user_field: user}  # 只查看自己的数据
    else:
        return {'id': None}  # 没有权限，返回空结果

def apply_data_permission_to_queryset(queryset, user, module, user_field='created_by'):
    """
    对查询集应用数据权限过滤
    
    Args:
        queryset: Django查询集
        user: 用户对象
        module: 模块名称
        user_field: 用户字段名
    
    Returns:
        QuerySet: 过滤后的查询集
    """
    data_filter = get_user_data_filter(user, module, user_field)
    if data_filter:
        return queryset.filter(**data_filter)
    return queryset

def apply_data_permission_to_list(data_list, user, module, user_field='username'):
    """
    对列表数据应用数据权限过滤
    
    Args:
        data_list: 数据列表
        user: 用户对象
        module: 模块名称
        user_field: 用户字段名
    
    Returns:
        list: 过滤后的数据列表
    """
    if can_view_all_data(user, module):
        return data_list  # 可以查看全部数据
    elif can_view_own_data(user, module):
        # 只返回用户自己的数据
        return [item for item in data_list if item.get(user_field) == user.username]
    else:
        return []  # 没有权限，返回空列表

# ==================== 基于公司、部门的权限控制函数 ====================

def get_user_company_department(user):
    """
    获取用户所属的公司和部门信息
    
    Args:
        user: 用户对象
    
    Returns:
        tuple: (company, department, position) 或 (None, None, None)
    """
    try:
        profile = UserProfile.objects.select_related('company', 'department', 'position').get(user=user)
        return profile.company, profile.department, profile.position
    except UserProfile.DoesNotExist:
        return None, None, None

def has_company_permission(user, permission_code):
    """
    检查用户是否有公司级别的权限
    
    Args:
        user: 用户对象
        permission_code: 权限代码
    
    Returns:
        bool: 是否有权限
    """
    if not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    # 首先检查角色权限
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    for user_role in user_roles:
        try:
            permission = Permission.objects.get(code=permission_code)
            if RolePermission.objects.filter(role=user_role.role, permission=permission).exists():
                return True
        except Permission.DoesNotExist:
            continue
    
    company, department, position = get_user_company_department(user)
    if not company:
        return False
    
    # 检查公司权限
    try:
        permission = Permission.objects.get(code=permission_code)
        if CompanyPermission.objects.filter(company=company, permission=permission).exists():
            return True
    except Permission.DoesNotExist:
        pass
    
    return False

def has_department_permission(user, permission_code):
    """
    检查用户是否有部门级别的权限
    
    Args:
        user: 用户对象
        permission_code: 权限代码
    
    Returns:
        bool: 是否有权限
    """
    if not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    company, department, position = get_user_company_department(user)
    if not department:
        return False
    
    # 检查部门权限
    try:
        permission = Permission.objects.get(code=permission_code)
        if DepartmentPermission.objects.filter(department=department, permission=permission).exists():
            return True
    except Permission.DoesNotExist:
        pass
    
    return False

def has_position_permission(user, permission_code):
    """
    检查用户是否有职位级别的权限
    
    Args:
        user: 用户对象
        permission_code: 权限代码
    
    Returns:
        bool: 是否有权限
    """
    if not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    company, department, position = get_user_company_department(user)
    if not position:
        return False
    
    # 检查职位权限
    try:
        permission = Permission.objects.get(code=permission_code)
        if PositionPermission.objects.filter(position=position, permission=permission).exists():
            return True
    except Permission.DoesNotExist:
        pass
    
    return False

def has_hierarchical_permission(user, permission_code):
    """
    检查用户是否有权限（仅基于角色权限）
    
    Args:
        user: 用户对象
        permission_code: 权限代码
    
    Returns:
        bool: 是否有权限
    """
    if not user.is_authenticated:
        return False
    
    # 超级管理员拥有所有权限
    if user.is_superuser:
        return True
    
    # 只检查角色权限，移除公司、部门、职位权限检查
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    for user_role in user_roles:
        try:
            permission = Permission.objects.get(code=permission_code)
            if RolePermission.objects.filter(role=user_role.role, permission=permission).exists():
                return True
        except Permission.DoesNotExist:
            continue
    
    return False

def get_user_data_filter_by_company_department(user, module, user_field='username'):
    """
    根据用户角色权限获取数据过滤条件（简化版，不再依赖公司部门）
    
    Args:
        user: 用户对象
        module: 模块名称
        user_field: 用户字段名
    
    Returns:
        dict: 过滤条件字典
    """
    # 获取权限代码
    permission_code = get_report_permission_code(module)
    
    # 简化权限检查逻辑，只基于角色权限
    # 检查是否有查看全部数据的权限
    if has_hierarchical_permission(user, f"{permission_code}_view_all"):
        return {}  # 返回空字典表示不过滤，可以查看所有数据
    
    # 检查是否有查看公司数据的权限（简化版，直接返回不过滤）
    if has_hierarchical_permission(user, f"{permission_code}_view_company"):
        return {}  # 简化处理，有公司权限就查看所有数据
    
    # 检查是否有查看部门数据的权限（简化版，直接返回不过滤）
    if has_hierarchical_permission(user, f"{permission_code}_view_department"):
        return {}  # 简化处理，有部门权限就查看所有数据
    
    # 检查是否有查看自己数据的权限
    if has_hierarchical_permission(user, f"{permission_code}_view_own"):
        return {user_field: user.username}
    
    # 如果没有找到任何相关权限，返回空结果
    return {'id': None}

def apply_company_department_permission_to_queryset(queryset, user, module, user_field='username'):
    """
    对查询集应用基于角色权限的数据过滤（简化版）
    
    Args:
        queryset: Django查询集
        user: 用户对象
        module: 模块名称
        user_field: 用户字段名
    
    Returns:
        QuerySet: 过滤后的查询集
    """
    data_filter = get_user_data_filter_by_company_department(user, module, user_field)
    if data_filter:
        return queryset.filter(**data_filter)
    return queryset

def get_user_permission_level(user, module):
    """
    获取用户对指定模块的权限级别（简化版）
    
    Args:
        user: 用户对象
        module: 模块名称
    
    Returns:
        str: 权限级别 ('none', 'all')
    """
    if not user.is_authenticated:
        return 'none'
    
    if user.is_superuser:
        return 'all'
    
    # 获取权限代码
    from home.config import get_report_module_code
    module_code = get_report_module_code(module)
    
    # 简化权限级别检查，只检查是否有查看权限
    if has_hierarchical_permission(user, f"{module_code}_view_all") or \
       has_hierarchical_permission(user, f"{module_code}_view_company") or \
       has_hierarchical_permission(user, f"{module_code}_view_department") or \
       has_hierarchical_permission(user, f"{module_code}_view_own"):
        return 'all'
    else:
        return 'none'

def can_edit_report(user, report, module):
    """
    检查用户是否可以编辑指定报表
    
    Args:
        user: 用户对象
        report: 报表对象
        module: 模块名称
    
    Returns:
        bool: 是否可以编辑
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # 检查编辑期限
    from datetime import datetime
    edit_limit = 7  # 默认7天
    try:
        from home.models import Parameter
        param = Parameter.objects.filter(id='report_edit_limit').first()
        if param and param.value:
            edit_limit = int(param.value)
    except:
        pass
    
    if report.date:
        days_diff = (datetime.now().date() - report.date).days
        if days_diff > edit_limit:
            return False  # 超过编辑期限，禁用编辑权限
    
    # 获取权限代码
    module_code = get_report_module_code(module)
    
    # 检查编辑权限 - 优先检查用户特定权限配置
    user_permissions_id = f'{module_code}_permissions_{user.username}'
    user_permissions_param = Parameter.objects.filter(id=user_permissions_id).first()
    
    has_edit_permission = False
    if user_permissions_param and user_permissions_param.value:
        try:
            import json
            user_permissions = json.loads(user_permissions_param.value)
            has_edit_permission = user_permissions.get('edit', False)
        except:
            pass
    
    # 如果没有用户特定权限配置，则检查角色权限
    if not has_edit_permission:
        has_edit_permission = has_hierarchical_permission(user, f"{module_code}_edit")
    
    if not has_edit_permission:
        return False
    
    # 检查数据权限
    permission_level = get_user_permission_level(user, module)
    
    # 如果用户有特定的权限配置，优先使用细粒度权限检查
    if user_permissions_param and user_permissions_param.value:
        return _check_granular_edit_permission(user, report, module)
    
    # 如果没有用户特定权限配置，则使用传统的权限级别检查
    if permission_level == 'none':
        return False
    else:
        # 进行细粒度权限检查，确保跨用户编辑权限被正确验证
        return _check_granular_edit_permission(user, report, module)

def _check_granular_edit_permission(user, report, module):
    """
    检查细粒度编辑权限
    
    Args:
        user: 当前用户
        report: 报表对象
        module: 模块名称
    
    Returns:
        bool: 是否可以编辑
    """
    # 1. 检查是否是数据录入者本人（最高优先级）
    if report.username == user.username:
        return True
    
    # 1.5. 特殊管理员用户可以直接编辑（临时解决方案）
    admin_users = ['GaoBieKeLe', 'yanyanzhao']
    if user.username in admin_users:
        return True
    
    # 2. 检查用户特定的权限配置
    try:
        from home.models import Parameter
        import json
        
        # 检查用户特定的权限配置
        module_code = get_report_module_code(module)
        user_permissions_id = f'{module_code}_permissions_{user.username}'
        user_permissions_param = Parameter.objects.filter(id=user_permissions_id).first()
        
        if user_permissions_param and user_permissions_param.value:
            try:
                user_permissions = json.loads(user_permissions_param.value)
                # 如果用户有跨用户编辑权限，允许编辑
                # 检查两种可能的键名：edit_others 和 edit-others
                edit_others = user_permissions.get('edit_others', False) or user_permissions.get('edit-others', False)
                if edit_others:
                    return True
                # 如果用户没有跨用户编辑权限，拒绝编辑他人数据
                else:
                    return False
            except:
                pass
        
        # 3. 检查跨用户编辑权限配置
        # 检查是否启用跨用户编辑
        cross_edit_param = Parameter.objects.filter(id='enable_cross_user_edit').first()
        if not cross_edit_param or cross_edit_param.value != 'true':
            return False
        
        # 3. 检查用户是否有跨用户编辑权限
        module_code = get_report_module_code(module)
        
        # 检查是否有跨用户编辑权限
        if not has_hierarchical_permission(user, f"{module_code}_edit_others"):
            return False
        
        # 4. 检查部门/公司级别的权限
        if _check_department_edit_permission(user, report):
            return True
        
        # 5. 检查角色级别的权限
        if _check_role_edit_permission(user, report, module):
            return True
            
    except Exception as e:
        # 如果配置读取失败，默认不允许跨用户编辑
        return False
    
    return False

def _check_department_edit_permission(user, report):
    """
    检查部门级别的编辑权限
    
    Args:
        user: 当前用户
        report: 报表对象
    
    Returns:
        bool: 是否有部门级编辑权限
    """
    try:
        # 获取用户和报表录入者的部门信息
        user_info = get_user_info(user.username)
        report_user_info = get_user_info(report.username)
        
        # 检查是否在同一部门
        if (user_info.get('department') and report_user_info.get('department') and 
            user_info['department'] == report_user_info['department']):
            return True
        
        # 检查是否在同一公司
        if (user_info.get('company') and report_user_info.get('company') and 
            user_info['company'] == report_user_info['company']):
            return True
            
    except Exception:
        pass
    
    return False

def _check_role_edit_permission(user, report, module):
    """
    检查角色级别的编辑权限
    
    Args:
        user: 当前用户
        report: 报表对象
        module: 模块名称
    
    Returns:
        bool: 是否有角色级编辑权限
    """
    try:
        # 检查用户是否有特定的管理角色
        user_info = get_user_info(user.username)
        user_roles = user_info.get('roles', [])
        
        # 定义可以跨用户编辑的角色
        cross_edit_roles = ['qc_manager', 'production_manager', 'quality_supervisor']
        
        for role in user_roles:
            if role in cross_edit_roles:
                return True
        
        # 检查是否有特定的模块管理权限
        module_code = get_report_module_code(module)
        
        # 检查是否有模块管理权限
        if has_hierarchical_permission(user, f"{module_code}_manage"):
            return True
            
    except Exception:
        pass
    
    return False

def can_delete_report(user, report, module):
    """
    检查用户是否可以删除指定报表
    
    Args:
        user: 用户对象
        report: 报表对象
        module: 模块名称
    
    Returns:
        bool: 是否可以删除
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # 检查编辑期限（删除权限也受编辑期限限制）
    from datetime import datetime
    edit_limit = 7  # 默认7天
    try:
        from home.models import Parameter
        param = Parameter.objects.filter(id='report_edit_limit').first()
        if param and param.value:
            edit_limit = int(param.value)
    except:
        pass
    
    if report.date:
        days_diff = (datetime.now().date() - report.date).days
        if days_diff > edit_limit:
            return False  # 超过编辑期限，禁用删除权限
    
    # 获取权限代码
    module_code = get_report_module_code(module)
    
    # 检查删除权限
    if not has_hierarchical_permission(user, f"{module_code}_delete"):
        return False
    
    # 删除权限通常与编辑权限相同
    return can_edit_report(user, report, module) 