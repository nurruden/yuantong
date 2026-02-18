from django.shortcuts import redirect, HttpResponse, render
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os
import requests
import logging
import urllib.parse
logger = logging.getLogger(__name__)


@csrf_exempt
def wechat_login(request):
    """
    企业微信登录视图
    自动检测是否在企业微信内，如果在则使用OAuth2授权（自动登录），否则使用扫码登录
    """
    try:
        # 如果用户已经登录，直接重定向到首页
        if request.user.is_authenticated:
            logger.info(f'User {request.user.username} already authenticated, redirecting to home')
            return redirect('home')
        
        # 获取企业微信配置
        corp_id = os.environ.get('WECHAT_CORP_ID')
        agent_id = os.environ.get('WECHAT_AGENT_ID')
        
        if not corp_id or not agent_id:
            logger.error('Missing WeChat configuration: WECHAT_CORP_ID or WECHAT_AGENT_ID')
            return render(request, 'login.html', {'error': '企业微信配置缺失，请联系管理员'})
        
        # 检测是否来自企业微信（企业微信的User-Agent包含 wxwork 或 micromessenger）
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_wechat_work = 'wxwork' in user_agent or ('micromessenger' in user_agent and 'wxwork' in user_agent)
        
        logger.info(f'User-Agent: {user_agent[:100]}..., is_wechat_work: {is_wechat_work}')
        
        # 构建回调URL
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        redirect_uri = f'{protocol}://{host}/wechat/callback/'
        redirect_uri_encoded = urllib.parse.quote(redirect_uri, safe='')
        
        # 获取 next 参数（登录后跳转的URL）
        next_url = request.GET.get('next', '')
        state = urllib.parse.quote(next_url, safe='') if next_url else 'STATE'
        
        # 如果在企业微信内，使用OAuth2授权（应用内授权，自动登录）
        if is_wechat_work:
            logger.info('Using WeChat Work OAuth2 authorization (internal app)')
            # 企业微信应用内授权URL
            auth_url = (
                f'https://open.weixin.qq.com/connect/oauth2/authorize?'
                f'appid={corp_id}&redirect_uri={redirect_uri_encoded}&response_type=code&'
                f'scope=snsapi_base&agentid={agent_id}&state={state}#wechat_redirect'
            )
            logger.info(f'Redirecting to WeChat Work OAuth2: {auth_url}')
            return redirect(auth_url)
        else:
            # 不在企业微信内，检查是否有扫码登录请求
            if request.GET.get('scan') == '1':
                # 如果是扫码登录请求，重定向到企业微信扫码登录
                logger.info('Using WeChat Work QR code login')
                auth_url = (
                    f'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?'
                    f'appid={corp_id}&agentid={agent_id}&redirect_uri={redirect_uri_encoded}&state={state}'
                )
                logger.info(f'Redirecting to WeChat QR login: {auth_url}')
                return redirect(auth_url)
            else:
                # 否则显示登录页面（包含用户名密码登录和扫码登录选项）
                logger.info('Displaying login page with password login option')
                return render(request, 'login.html', {'next': next_url})
        
    except Exception as e:
        logger.error(f'Error in wechat_login: {str(e)}', exc_info=True)
        return render(request, 'login.html', {'error': f'登录失败: {str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class AuthView(View):
    """企业微信授权视图（备用）"""
    def get(self, request):
        try:
            corp_id = os.environ.get('WECHAT_CORP_ID')
            app_secret = os.environ.get('WECHAT_APP_SECRET')
            agent_id = os.environ.get('WECHAT_AGENT_ID')
            
            if not corp_id or not app_secret or not agent_id:
                logger.error('Missing WeChat configuration')
                return HttpResponse('企业微信配置缺失', status=500)
            
            # 构建回调URL
            protocol = 'https' if request.is_secure() else 'http'
            host = request.get_host()
            redirect_uri = f'{protocol}://{host}/wechat/callback/'
            redirect_uri = urllib.parse.quote(redirect_uri, safe='')
            
            redirect_url = (
                f'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?'
                f'appid={corp_id}&agentid={agent_id}&redirect_uri={redirect_uri}&state=STATE'
            )
            return redirect(redirect_url)
        except Exception as e:
            logger.error(f'Error in AuthView: {str(e)}', exc_info=True)
            return HttpResponse(f'授权失败: {str(e)}', status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AuthCallbackView(View):
    """企业微信回调视图（别名：WeChatCallbackView）"""
    def get(self, request):
        try:
            code = request.GET.get('code')
            if not code:
                logger.error('Missing code parameter in WeChat callback')
                return render(request, 'login.html', {'error': '授权失败：缺少授权码'})
            
            logger.info(f'Processing WeChat callback with code: {code}')
            
            # 获取企业微信配置
            corp_id = os.environ.get('WECHAT_CORP_ID')
            app_secret = os.environ.get('WECHAT_APP_SECRET')
            
            if not corp_id or not app_secret:
                logger.error('Missing WeChat configuration: WECHAT_CORP_ID or WECHAT_APP_SECRET')
                return render(request, 'login.html', {'error': '企业微信配置缺失，请联系管理员'})
            
            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={app_secret}'
            token_resp = requests.get(token_url, timeout=10)
            token_resp.raise_for_status()
            token_data = token_resp.json()
            
            if token_data.get('errcode') != 0:
                logger.error(f'Failed to get WeChat token: {token_data}')
                return render(request, 'login.html', {'error': f'获取token失败: {token_data.get("errmsg", "未知错误")}'})
            
            access_token = token_data.get('access_token')
            
            # 获取用户信息
            user_url = f'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={access_token}&code={code}'
            user_resp = requests.get(user_url, timeout=10)
            user_resp.raise_for_status()
            user_data = user_resp.json()
            
            if user_data.get('errcode') != 0:
                logger.error(f'Failed to get WeChat user info: {user_data}')
                return render(request, 'login.html', {'error': f'获取用户信息失败: {user_data.get("errmsg", "未知错误")}'})
            
            userid = user_data.get('UserId')
            if not userid:
                logger.error(f'No UserId in WeChat user data: {user_data}')
                return render(request, 'login.html', {'error': '获取用户ID失败'})
            
            # 创建或获取用户
            user, created = User.objects.get_or_create(username=userid)
            
            # 如果是新用户，自动分配普通用户角色
            if created:
                try:
                    from system.models import Role, UserRole
                    normal_user_role = Role.objects.filter(name='普通用户').first()
                    if normal_user_role:
                        UserRole.objects.create(user=user, role=normal_user_role)
                        logger.info(f'Assigned normal user role to new user {userid}')
                    else:
                        logger.warning(f'Normal user role not found for user {userid}')
                except Exception as e:
                    logger.error(f'Error assigning role to user {userid}: {str(e)}')
            
            # 登录用户
            login(request, user)
            logger.info(f'User {userid} logged in successfully')
            
            # 重定向到首页
            return redirect('home')
            
        except Exception as e:
            logger.error(f'认证失败: {str(e)}', exc_info=True)
            return render(request, 'login.html', {'error': f'登录失败: {str(e)}'})


# 别名，用于兼容性
WeChatCallbackView = AuthCallbackView


@csrf_exempt
def custom_logout(request):
    """
    自定义登出视图
    """
    try:
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logout(request)
        logger.info(f'User {username} logged out')
        return redirect('login')
    except Exception as e:
        logger.error(f'Error in custom_logout: {str(e)}', exc_info=True)
        return redirect('login')


@method_decorator(csrf_exempt, name='dispatch')
class WeChatMessageReceiveView(View):
    """
    企业微信消息接收视图
    用于接收企业微信推送的消息
    """
    def post(self, request):
        try:
            # 这里可以处理企业微信推送的消息
            # 目前仅记录日志
            logger.info(f'Received WeChat message: {request.body.decode("utf-8")}')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f'Error in WeChatMessageReceiveView.post: {str(e)}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    def get(self, request):
        """
        企业微信消息验证（用于配置回调URL时的验证）
        """
        try:
            msg_signature = request.GET.get('msg_signature', '')
            timestamp = request.GET.get('timestamp', '')
            nonce = request.GET.get('nonce', '')
            echostr = request.GET.get('echostr', '')
            
            logger.info(f'WeChat message verification: msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}')
            
            # 这里应该实现消息验证逻辑
            # 目前直接返回echostr
            return HttpResponse(echostr)
        except Exception as e:
            logger.error(f'Error in WeChatMessageReceiveView.get: {str(e)}', exc_info=True)
            return HttpResponse('error', status=500)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class WeChatUserListAPI(View):
    """
    企业微信用户列表API
    获取企业微信通讯录中的用户列表
    """
    def get(self, request):
        try:
            # 获取企业微信配置
            corp_id = os.environ.get('WECHAT_CORP_ID')
            contact_secret = os.environ.get('WECHAT_CONTACT_SECRET')
            
            if not corp_id or not contact_secret:
                logger.error('Missing WeChat configuration: WECHAT_CORP_ID or WECHAT_CONTACT_SECRET')
                return JsonResponse({
                    'status': 'error',
                    'message': '企业微信配置缺失',
                    'users': []
                })
            
            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={contact_secret}'
            token_resp = requests.get(token_url, timeout=10)
            token_resp.raise_for_status()
            token_data = token_resp.json()
            
            if token_data.get('errcode') != 0:
                logger.error(f'Failed to get WeChat token: {token_data}')
                return JsonResponse({
                    'status': 'error',
                    'message': f'获取token失败: {token_data.get("errmsg", "未知错误")}',
                    'users': []
                })
            
            access_token = token_data.get('access_token')
            
            # 获取部门列表
            dept_url = f'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={access_token}'
            dept_resp = requests.get(dept_url, timeout=10)
            dept_resp.raise_for_status()
            dept_data = dept_resp.json()
            
            if dept_data.get('errcode') != 0:
                logger.error(f'Failed to get departments: {dept_data}')
                return JsonResponse({
                    'status': 'error',
                    'message': f'获取部门列表失败: {dept_data.get("errmsg", "未知错误")}',
                    'users': []
                })
            
            # 获取所有部门的用户
            users = []
            departments = dept_data.get('department', [])
            
            for dept in departments:
                dept_id = dept.get('id')
                # 获取部门成员
                user_url = f'https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={access_token}&department_id={dept_id}'
                user_resp = requests.get(user_url, timeout=10)
                user_resp.raise_for_status()
                user_data = user_resp.json()
                
                if user_data.get('errcode') == 0:
                    user_list = user_data.get('userlist', [])
                    users.extend(user_list)
            
            # 去重（按userid）
            seen = set()
            unique_users = []
            for user in users:
                userid = user.get('userid')
                if userid and userid not in seen:
                    seen.add(userid)
                    unique_users.append({
                        'userid': userid,
                        'name': user.get('name', ''),
                        'mobile': user.get('mobile', ''),
                        'department': user.get('department', []),
                        'position': user.get('position', ''),
                        'email': user.get('email', ''),
                    })
            
            logger.info(f'Retrieved {len(unique_users)} WeChat users')
            return JsonResponse({
                'status': 'success',
                'users': unique_users
            })
            
        except Exception as e:
            logger.error(f'Error in WeChatUserListAPI: {str(e)}', exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'users': []
            })

@method_decorator(csrf_exempt, name='dispatch')
class SyncDepartmentsView(View):
    """部门同步视图"""
    def get(self, request):
        try:
            # 获取企业微信配置
            corp_id = os.environ.get('WECHAT_CORP_ID')
            contact_secret = os.environ.get('WECHAT_CONTACT_SECRET')
            
            if not corp_id or not contact_secret:
                logger.error('Missing WeChat configuration for department sync')
                return HttpResponse('企业微信配置缺失', status=500)
            
            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={contact_secret}'
            token_resp = requests.get(token_url, timeout=10)
            token_resp.raise_for_status()
            token_data = token_resp.json()
            
            if token_data.get('errcode') != 0:
                logger.error(f'Failed to get WeChat token: {token_data}')
                return HttpResponse(f'获取token失败: {token_data.get("errmsg", "未知错误")}', status=500)
            
            access_token = token_data.get('access_token')
            
            # 获取部门列表
            res = requests.get(f'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={access_token}', timeout=10)
            res.raise_for_status()
            dept_data = res.json()
            
            if dept_data.get('errcode') != 0:
                logger.error(f'Failed to get departments: {dept_data}')
                return HttpResponse(f'获取部门列表失败: {dept_data.get("errmsg", "未知错误")}', status=500)
            
            # TODO: 实现部门同步逻辑
            logger.info(f'Retrieved {len(dept_data.get("department", []))} departments')
            return JsonResponse({'status': 'success', 'departments': dept_data.get('department', [])})
            
        except Exception as e:
            logger.error(f'部门同步失败: {str(e)}', exc_info=True)
            return HttpResponse(f'部门同步失败: {str(e)}', status=500)
