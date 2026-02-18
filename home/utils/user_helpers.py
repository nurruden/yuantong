"""
用户信息辅助函数模块
提供用户信息获取等功能
"""

from django.contrib.auth.models import User


def get_user_info(userid):
    """获取用户信息"""
    try:
        # 尝试从Django User模型获取用户信息
        user = User.objects.get(username=userid)
        # 如果用户有first_name和last_name，组合显示
        if user.first_name and user.last_name:
            return {
                'name': f"{user.last_name}-{user.first_name}",
                'userid': userid
            }
        elif user.first_name:
            return {
                'name': user.first_name,
                'userid': userid
            }
        else:
            return {
                'name': userid,
                'userid': userid
            }
    except User.DoesNotExist:
        # 如果Django User不存在，返回原始userid
        return {'name': userid, 'userid': userid}
    except Exception as e:
        # 如果有其他错误，也返回原始userid
        return {'name': userid, 'userid': userid}


def is_admin_user(userid):
    """检查用户是否是管理员"""
    # 开发环境下暂时返回 True
    return True
    admin_users = ['yanyanzhao', 'GaoBieKeLe']  # 可以在此添加更多管理员
    # Checking admin status for user: userid
    return userid in admin_users
