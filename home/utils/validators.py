"""
数据验证工具模块
提供基于Django模型字段定义的数据验证功能
"""

from django.db.models.fields import NOT_PROVIDED
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, time


def validate_field_by_model(model_class, field_name, value, field_display_name=None):
    """
    根据Django模型字段定义校验字段值
    
    Args:
        model_class: Django模型类
        field_name: 字段名
        value: 要校验的值
        field_display_name: 字段显示名称（用于错误提示）
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if field_display_name is None:
        field_display_name = field_name
    
    # 如果值为None或空，且字段允许null/blank或有默认值，则通过校验
    if value is None or (isinstance(value, str) and value.strip() == ''):
        try:
            field = model_class._meta.get_field(field_name)
            # 如果字段允许null或blank，则允许为空
            if field.null or field.blank:
                return True, None
            # 如果字段有默认值（包括callable），也允许为空，因为Django会自动使用默认值
            if hasattr(field, 'default'):
                # 对于NOT_PROVIDED，表示没有默认值
                if field.default is not NOT_PROVIDED:
                    return True, None
            # 没有默认值且不允许null/blank的字段才报错
            return False, f'字段"{field_display_name}"不能为空'
        except:
            return True, None  # 如果字段不存在，跳过校验
    
    try:
        field = model_class._meta.get_field(field_name)
    except:
        return True, None  # 字段不存在，跳过校验
    
    # 根据字段类型进行校验
    field_type = type(field).__name__
    
    # CharField: 校验最大长度
    if field_type == 'CharField':
        max_length = field.max_length
        if isinstance(value, str):
            if len(value) > max_length:
                return False, f'字段"{field_display_name}"值"{value[:50]}{"..." if len(value) > 50 else ""}"超过最大长度{max_length}字符（实际长度：{len(value)}）'
        else:
            value_str = str(value)
            if len(value_str) > max_length:
                return False, f'字段"{field_display_name}"值"{value_str[:50]}{"..." if len(value_str) > 50 else ""}"超过最大长度{max_length}字符（实际长度：{len(value_str)}）'
    
    # TextField: 无长度限制，但需要是字符串
    elif field_type == 'TextField':
        if not isinstance(value, str):
            return False, f'字段"{field_display_name}"必须是文本类型'
    
    # DateField: 校验日期格式
    elif field_type == 'DateField':
        if not isinstance(value, (date, datetime)):
            if isinstance(value, str):
                try:
                    datetime.strptime(value.strip(), '%Y-%m-%d')
                except:
                    try:
                        datetime.strptime(value.strip(), '%Y/%m/%d')
                    except:
                        return False, f'字段"{field_display_name}"值"{value}"日期格式错误，支持的格式：YYYY-MM-DD 或 YYYY/MM/DD'
    
    # TimeField: 校验时间格式
    elif field_type == 'TimeField':
        if not isinstance(value, (time, datetime)):
            if isinstance(value, str):
                try:
                    datetime.strptime(value.strip(), '%H:%M')
                except:
                    try:
                        datetime.strptime(value.strip(), '%H:%M:%S')
                    except:
                        return False, f'字段"{field_display_name}"值"{value}"时间格式错误，支持的格式：HH:MM 或 HH:MM:SS'
    
    # FloatField: 校验浮点数
    elif field_type in ['FloatField', 'NullableFloatField']:
        try:
            float_val = float(value)
            if abs(float_val) == float('inf') or float_val != float_val:  # 检查inf和NaN
                return False, f'字段"{field_display_name}"值"{value}"不是有效的数字'
        except (ValueError, TypeError):
            return False, f'字段"{field_display_name}"值"{value}"无法转换为数字类型'
    
    # DecimalField: 校验精度（max_digits和decimal_places）
    elif field_type == 'DecimalField':
        try:
            # 先尝试转换为Decimal，保持精度
            # 如果已经是字符串，直接转换为Decimal
            if isinstance(value, str):
                # 去除前后空格
                value_str = value.strip()
                # 尝试转换为Decimal
                try:
                    decimal_val = Decimal(value_str)
                except (InvalidOperation, ValueError):
                    # 如果直接转换失败，尝试先转换为float再转Decimal（兼容科学计数法等）
                    try:
                        decimal_val = Decimal(str(float(value_str)))
                    except (ValueError, TypeError):
                        return False, f'字段"{field_display_name}"值"{value}"无法转换为数字'
            elif isinstance(value, (int, float)):
                # 如果是数字类型，转换为字符串再转Decimal，避免精度丢失
                decimal_val = Decimal(str(value))
            else:
                # 其他类型，尝试直接转换
                decimal_val = Decimal(str(value))
            
            # 使用Decimal的as_tuple()方法获取精确的位数信息
            # as_tuple()返回 (sign, digits, exponent)
            # sign: 0表示正数，1表示负数
            # digits: 数字元组，例如 (1, 0, 0, 2, 3) 表示 10023
            # exponent: 指数，例如 -4 表示小数点后4位
            sign, digits, exponent = decimal_val.as_tuple()
            
            # 计算总位数（不包括小数点）
            total_digits = len(digits)
            
            # 计算小数位数
            # 如果exponent是负数，表示有小数部分
            if exponent < 0:
                decimal_places = abs(exponent)
            else:
                decimal_places = 0
            
            max_digits = field.max_digits
            decimal_places_limit = field.decimal_places
            
            if total_digits > max_digits:
                return False, f'字段"{field_display_name}"值"{value}"总位数{total_digits}超过限制{max_digits}位'
            if decimal_places > decimal_places_limit:
                return False, f'字段"{field_display_name}"值"{value}"小数位数{decimal_places}超过限制{decimal_places_limit}位'
        except (ValueError, TypeError, InvalidOperation) as e:
            return False, f'字段"{field_display_name}"值"{value}"无法转换为数字: {str(e)}'
    
    # IntegerField: 校验整数
    elif field_type == 'IntegerField':
        try:
            int(value)
        except (ValueError, TypeError):
            return False, f'字段"{field_display_name}"值"{value}"无法转换为整数'
    
    # BooleanField: 校验布尔值
    elif field_type == 'BooleanField':
        if value not in [True, False, 1, 0, 'True', 'False', 'true', 'false', '1', '0']:
            return False, f'字段"{field_display_name}"值"{value}"不是有效的布尔值'
    
    # ForeignKey: 校验外键（如果有choices或需要验证存在性）
    elif field_type == 'ForeignKey':
        # 这里可以添加外键存在性校验，但通常ForeignKey字段在创建时会自动处理
        pass
    
    # 校验choices（如果有）
    if hasattr(field, 'choices') and field.choices:
        valid_choices = [choice[0] for choice in field.choices]
        if value not in valid_choices:
            return False, f'字段"{field_display_name}"值"{value}"无效，必须是以下值之一：{", ".join(map(str, valid_choices))}'
    
    return True, None
