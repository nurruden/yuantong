"""
微信认证相关视图
包含企业微信登录、回调、消息接收等功能
"""

# 导入必要的模块
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import os
import json
import logging
import urllib.parse
import hashlib
import requests

logger = logging.getLogger(__name__)

# ==================== 微信认证相关视图 ===================

class WeChatUserListAPI(View):
    def get(self, request):
        """获取企业微信用户列表，用于权限配置"""
        try:
            corpid = os.environ.get('WECHAT_CORP_ID')
            corpsecret = os.environ.get('WECHAT_CONTACT_SECRET')
            
            if not corpid or not corpsecret:
                # 如果没有企业微信配置，返回系统现有用户
                from django.contrib.auth.models import User
                users = []
                for user in User.objects.all():
                    users.append({
                        'userid': user.username,
                        'name': user.first_name or user.username,
                        'avatar': ''  # 默认头像为空
                    })
                return JsonResponse({'success': True, 'users': users})
            
            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}'
            token_resp = requests.get(token_url, timeout=5)
            token_data = token_resp.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                # 如果获取access_token失败，回退到系统用户
                from django.contrib.auth.models import User
                users = []
                for user in User.objects.all():
                    users.append({
                        'userid': user.username,
                        'name': user.first_name or user.username,
                        'avatar': ''
                    })
                return JsonResponse({'success': True, 'users': users})
            
            # 拉取通讯录用户
            user_url = f'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token={access_token}&department_id=1&fetch_child=1'
            user_resp = requests.get(user_url, timeout=5)
            user_data = user_resp.json()
            
            if user_data.get('errcode') == 0:
                return JsonResponse({'success': True, 'users': user_data.get('userlist', [])})
            else:
                # 如果企业微信API调用失败，回退到系统用户
                from django.contrib.auth.models import User
                users = []
                for user in User.objects.all():
                    users.append({
                        'userid': user.username,
                        'name': user.first_name or user.username,
                        'avatar': ''
                    })
                return JsonResponse({'success': True, 'users': users})
                
        except Exception as e:
            # 发生异常时回退到系统用户
            from django.contrib.auth.models import User
            users = []
            for user in User.objects.all():
                users.append({
                    'userid': user.username,
                    'name': user.first_name or user.username,
                    'avatar': ''
                })
            return JsonResponse({'success': True, 'users': users})


# 原土入库删除接口
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests



# 原土入库视图

# 登录视图（必须为公开，不可加 login_required，否则会重定向死循环）
def wechat_login(request):
    import logging
    logger = logging.getLogger(__name__)

    # 如果用户已经登录，直接重定向到首页
    if request.user.is_authenticated:
        logger.info(f'User {request.user.username} already authenticated, redirecting to home')
        return redirect('/')

    next_url = request.GET.get('next', '/')
    logger.info(f'wechat_login called, next_url: {next_url}')

    # 检测是否来自企业微信
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_wechat = 'micromessenger' in user_agent or 'wxwork' in user_agent
    logger.info(f'User-Agent: {user_agent[:100]}..., is_wechat: {is_wechat}')

    # 获取配置
    corp_id = os.environ.get('WECHAT_CORP_ID')
    corp_secret = os.environ.get('WECHAT_APP_SECRET')  # 使用 APP_SECRET
    agent_id = os.environ.get('WECHAT_AGENT_ID')
    
    # 检查配置是否完整
    if not corp_id or not corp_secret or not agent_id:
        logger.error('Missing WeChat configuration')
        return render(request, 'error.html', {
            'message': '系统配置错误：缺少企业微信配置，请联系管理员'
        })

    # 如果来自企业微信，使用应用内授权
    if is_wechat:
        logger.info('Using WeChat Work internal authorization')
        try:
            # 构建企业微信OAuth授权URL
            redirect_uri = request.build_absolute_uri('/wechat/callback/')
            encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
            encoded_state = urllib.parse.quote(next_url, safe='')

            auth_url = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={corp_id}&redirect_uri={encoded_redirect_uri}&response_type=code&scope=snsapi_base&agentid={agent_id}&state={encoded_state}#wechat_redirect'
            
            logger.info(f'Redirecting to WeChat Work OAuth: {auth_url}')
            
            # 使用JavaScript重定向
            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>正在跳转...</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
                <div style="text-align: center; padding: 50px;">
                    <p>正在跳转到授权页面...</p>
                </div>
                <script>
                    console.log('Redirecting to WeChat OAuth:', '{auth_url}');
                    window.location.href = '{auth_url}';
                </script>
            </body>
            </html>
            '''
            return HttpResponse(html_content)
        except Exception as e:
            logger.error(f'Error in WeChat Work authorization: {str(e)}')
            return render(request, 'error.html', {
                'message': f'授权失败：{str(e)}'
            })

    # 如果是扫码登录请求
    if request.GET.get('scan') == '1':
        logger.info('Using WeChat Work QR code login')
        try:
            redirect_uri = request.build_absolute_uri('/wechat/callback/')
            encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
            encoded_state = urllib.parse.quote(next_url, safe='')
            
            auth_url = f'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid={corp_id}&agentid={agent_id}&redirect_uri={encoded_redirect_uri}&state={encoded_state}'
            
            logger.info(f'Redirecting to WeChat QR login: {auth_url}')
            return redirect(auth_url)
        except Exception as e:
            logger.error(f'Error in WeChat QR login: {str(e)}')
            return render(request, 'error.html', {
                'message': f'扫码登录失败：{str(e)}'
            })

    # 显示登录页面
    logger.info('Displaying login page')
    return render(request, 'login.html')


from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User


class WeChatCallbackView(View):
    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)

        code = request.GET.get('code')
        state = request.GET.get('state', '/')

        logger.info(f'=== WeChat Callback Started ===')
        logger.info(f'Received callback with code: {code}, state: {state}')
        logger.info(f'Request URL: {request.build_absolute_uri()}')
        logger.info(f'Request args: {dict(request.GET)}')

        if not code:
            logger.error('No code in callback request')
            return render(request, 'error.html', {
                'message': '授权失败：未收到授权码'
            })

        try:
            # 获取access token
            corp_id = os.environ.get('WECHAT_CORP_ID')
            corp_secret = os.environ.get('WECHAT_APP_SECRET')  # 使用 APP_SECRET

            if not corp_id or not corp_secret:
                logger.error('Missing WeChat configuration')
                return render(request, 'error.html', {
                    'message': '系统配置错误：缺少企业微信配置，请联系管理员'
                })

            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}'
            logger.info(f'Requesting access token from: {token_url.replace(corp_secret, "***")}')

            token_resp = requests.get(token_url, timeout=10)
            token_data = token_resp.json()
            logger.info(f'Token response: {token_data}')

            if token_data.get('errcode') != 0:
                raise Exception(f'获取access_token失败: {token_data}')

            access_token = token_data.get('access_token')
            if not access_token:
                raise Exception('未获取到access_token')

            # 使用code获取用户信息
            user_url = f"https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo?access_token={access_token}&code={code}"
            logger.info(f'Requesting user info from: {user_url}')

            user_resp = requests.get(user_url, timeout=10)
            user_info = user_resp.json()
            logger.info(f'User info response: {user_info}')

            if user_info.get('errcode') != 0:
                raise Exception(f'获取用户信息失败: {user_info}')

            userid = user_info.get('userid')
            if not userid:
                raise Exception('未获取到用户ID')

            # 获取用户详细信息
            detail_url = f"https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={userid}"
            logger.info(f'Requesting user details from: {detail_url}')

            detail_resp = requests.get(detail_url, timeout=10)
            user_detail = detail_resp.json()
            logger.info(f'User detail response: {user_detail}')

            if user_detail.get('errcode') != 0:
                raise Exception(f'获取用户详细信息失败: {user_detail}')

            # 创建或更新用户
            user, created = User.objects.get_or_create(
                username=userid,
                defaults={
                    'first_name': user_detail.get('name', ''),
                    'last_name': user_detail.get('department', ''),
                    'email': user_detail.get('email', f'{userid}@work.weixin.qq.com')
                }
            )

            if not created:
                user.first_name = user_detail.get('name', '')
                user.last_name = user_detail.get('department', '')
                user.email = user_detail.get('email', f'{userid}@work.weixin.qq.com')
                user.save()

            # 如果是新用户，自动分配普通用户角色
            if created:
                try:
                    from system.models import Role, UserRole
                    # 获取普通用户角色
                    normal_user_role = Role.objects.filter(name='普通用户').first()
                    if normal_user_role:
                        # 创建用户角色关联
                        UserRole.objects.create(user=user, role=normal_user_role)
                        logger.info(f'Assigned normal user role to new user {userid}')
                    else:
                        logger.warning(f'Normal user role not found for user {userid}')
                except Exception as e:
                    logger.error(f'Error assigning role to user {userid}: {str(e)}')

            # 登录用户
            login(request, user)
            logger.info(f'User {userid} logged in successfully')

            # 重定向到原始请求的页面
            return redirect(state)

        except Exception as e:
            logger.error(f'Error in WeChat callback: {str(e)}', exc_info=True)
            return render(request, 'error.html', {
                'message': f'登录失败：{str(e)}'
            })


# 检查是否为管理员
# is_admin_user 已移动到 home.utils.user_helpers
# has_system_settings_permission 已移动到 home.utils.permissions
# filter_menu_by_permission 已移动到 home.utils.permissions
class WeChatMessageReceiveView(View):
    """
    企业微信消息接收URL验证视图
    用于验证企业微信应用设置的接收消息URL
    当在企业微信管理后台设置接收消息URL时，企业微信会发送GET请求进行验证
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        处理企业微信URL验证请求
        企业微信会发送GET请求，参数包括：
        - msg_signature: 企业微信加密签名
        - timestamp: 时间戳
        - nonce: 随机数
        - echostr: 加密的随机字符串（如果使用加密模式）或明文随机字符串（如果使用明文模式）
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 获取请求参数
        msg_signature = request.GET.get('msg_signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')
        
        logger.info(f'=== 企业微信消息接收URL验证 ===')
        logger.info(f'收到验证请求 - msg_signature: {msg_signature}, timestamp: {timestamp}, nonce: {nonce}, echostr长度: {len(echostr)}')
        logger.info(f'请求完整URL: {request.build_absolute_uri()}')
        logger.info(f'所有GET参数: {dict(request.GET)}')
        
        # 检查必要参数
        if not all([msg_signature, timestamp, nonce, echostr]):
            missing_params = []
            if not msg_signature: missing_params.append('msg_signature')
            if not timestamp: missing_params.append('timestamp')
            if not nonce: missing_params.append('nonce')
            if not echostr: missing_params.append('echostr')
            logger.error(f'缺少必要参数: {", ".join(missing_params)}')
            return HttpResponse(f'缺少必要参数: {", ".join(missing_params)}', status=400)
        
        try:
            # 获取配置的Token（接收消息的Token）
            # 这个Token需要在企业微信管理后台设置接收消息时配置
            token = os.environ.get('WECHAT_MESSAGE_TOKEN', '')
            
            if not token:
                logger.error('未配置WECHAT_MESSAGE_TOKEN环境变量')
                return HttpResponse('服务器配置错误：未设置接收消息Token', status=500)
            
            logger.info(f'Token已配置，长度: {len(token)}')
            
            # 检查是否配置了EncodingAESKey（用于判断是加密模式还是明文模式）
            encoding_aes_key = os.environ.get('WECHAT_ENCODING_AES_KEY', '')
            corp_id = os.environ.get('WECHAT_CORP_ID', '')
            
            if encoding_aes_key and corp_id:
                # 使用加密模式
                logger.info('使用加密模式进行验证和解密')
                logger.info(f'EncodingAESKey已配置，长度: {len(encoding_aes_key)}')
                logger.info(f'CorpID: {corp_id}')
                try:
                    from wechatpy.enterprise.crypto import WeChatCrypto
                    crypto = WeChatCrypto(token, encoding_aes_key, corp_id)
                    # 使用WeChatCrypto的check_signature方法验证签名
                    # 如果签名验证通过，check_signature会返回解密后的echostr
                    # 如果签名验证失败，会抛出异常
                    try:
                        decrypted_echostr = crypto.check_signature(msg_signature, timestamp, nonce, echostr)
                        logger.info(f'签名验证成功，解密后的echostr: {decrypted_echostr}')
                        # 返回纯文本格式的echostr，不包含引号或其他字符
                        return HttpResponse(decrypted_echostr, content_type='text/plain')
                    except ValueError as e:
                        # check_signature验证失败会抛出ValueError
                        logger.error(f'签名验证失败（使用WeChatCrypto）: {str(e)}')
                        logger.error(f'请检查WECHAT_MESSAGE_TOKEN和WECHAT_ENCODING_AES_KEY是否与企业微信管理后台配置一致')
                        return HttpResponse('签名验证失败', status=403)
                except Exception as e:
                    logger.error(f'加密模式处理失败: {str(e)}', exc_info=True)
                    # 如果解密失败，可能是配置错误，返回错误信息
                    return HttpResponse(f'解密失败: {str(e)}', status=500)
            else:
                # 使用明文模式
                logger.info('使用明文模式进行验证')
                # 企业微信明文模式签名算法：将token、timestamp、nonce三个参数进行字典序排序
                # 然后拼接成一个字符串，进行sha1加密
                # 最后将加密后的字符串与msg_signature对比
                
                # 1. 对token、timestamp、nonce进行字典序排序
                sorted_params = sorted([token, timestamp, nonce])
                
                # 2. 拼接成字符串
                combined_string = ''.join(sorted_params)
                
                # 3. 进行sha1加密
                sha1_hash = hashlib.sha1(combined_string.encode('utf-8')).hexdigest()
                
                logger.info(f'签名计算 - 排序后的参数: {sorted_params}')
                logger.info(f'签名计算 - 拼接字符串: {combined_string}')
                logger.info(f'签名计算 - SHA1哈希: {sha1_hash}')
                logger.info(f'签名对比 - 期望: {sha1_hash}, 实际: {msg_signature}')
                
                # 4. 与msg_signature对比
                if sha1_hash != msg_signature:
                    logger.error(f'签名验证失败 - 期望: {sha1_hash}, 实际: {msg_signature}')
                    logger.error(f'请检查WECHAT_MESSAGE_TOKEN是否与企业微信管理后台配置的Token一致')
                    return HttpResponse('签名验证失败', status=403)
                
                logger.info('签名验证成功，返回echostr')
                # 返回纯文本格式的echostr，不包含引号或其他字符
                return HttpResponse(echostr, content_type='text/plain')
                
        except Exception as e:
            logger.error(f'处理验证请求时出错: {str(e)}', exc_info=True)
            return HttpResponse(f'服务器错误: {str(e)}', status=500)
    
    def post(self, request):
        """
        处理企业微信审批状态通知事件
        企业微信会以POST请求的方式推送审批状态变化事件
        请求参数包括：
        - msg_signature: 企业微信加密签名
        - timestamp: 时间戳
        - nonce: 随机数
        - 消息体: 加密的XML格式数据（如果使用加密模式）
        """
        import logging
        import xml.etree.ElementTree as ET
        import sys
        
        logger = logging.getLogger(__name__)
        
        # 使用标准错误输出确保日志被记录（gunicorn会捕获stderr）
        print("=" * 80, file=sys.stderr)
        print("POST请求到达 WeChatMessageReceiveView.post()", file=sys.stderr)
        print(f"时间: {datetime.now()}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        sys.stderr.flush()  # 强制刷新输出
        
        # 获取请求参数
        msg_signature = request.GET.get('msg_signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        
        # 立即记录日志（使用logger.error确保记录）
        logger.error("=" * 80)
        logger.error("POST请求到达 WeChatMessageReceiveView.post()")
        logger.error(f"时间: {datetime.now()}")
        logger.error(f"GET参数: msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")
        logger.error("=" * 80)
        
        # 同时输出到stderr
        print(f"GET参数: msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}", file=sys.stderr)
        sys.stderr.flush()
        
        # 获取消息体
        try:
            encrypted_msg = request.body.decode('utf-8')
        except Exception as e:
            logger.error(f'读取消息体失败: {str(e)}')
            encrypted_msg = ''
        
        # 强制输出日志到error.log（使用error级别确保记录）
        logger.error(f'=== 企业微信审批状态通知事件 ===')
        logger.error(f'收到审批事件 - msg_signature: {msg_signature}, timestamp: {timestamp}, nonce: {nonce}')
        logger.error(f'请求完整URL: {request.build_absolute_uri()}')
        logger.error(f'请求方法: {request.method}')
        logger.error(f'消息体长度: {len(encrypted_msg)}')
        logger.error(f'消息体前200字符: {encrypted_msg[:200] if encrypted_msg else "空"}')
        logger.error(f'所有GET参数: {dict(request.GET)}')
        
        # 检查必要参数
        if not all([msg_signature, timestamp, nonce]):
            missing_params = []
            if not msg_signature: missing_params.append('msg_signature')
            if not timestamp: missing_params.append('timestamp')
            if not nonce: missing_params.append('nonce')
            logger.error(f'缺少必要参数: {", ".join(missing_params)}')
            return HttpResponse('缺少必要参数', status=400)
        
        if not encrypted_msg:
            logger.error('消息体为空，无法处理审批事件')
            logger.error(f'请求头: {dict(request.headers)}')
            logger.error(f'Content-Type: {request.content_type}')
            logger.error(f'Content-Length: {request.META.get("CONTENT_LENGTH", "N/A")}')
            # 即使消息体为空，也返回success，避免企业微信重复推送
            return HttpResponse('success', content_type='text/plain')
        
        try:
            # 获取配置的Token和EncodingAESKey
            token = os.environ.get('WECHAT_MESSAGE_TOKEN', '')
            encoding_aes_key = os.environ.get('WECHAT_ENCODING_AES_KEY', '')
            corp_id = os.environ.get('WECHAT_CORP_ID', '')
            
            if not token:
                logger.error('未配置WECHAT_MESSAGE_TOKEN环境变量')
                return HttpResponse('服务器配置错误：未设置接收消息Token', status=500)
            
            if not encoding_aes_key or not corp_id:
                logger.error('未配置WECHAT_ENCODING_AES_KEY或WECHAT_CORP_ID，审批事件需要使用加密模式')
                return HttpResponse('服务器配置错误：审批事件需要使用加密模式', status=500)
            
            # 使用加密模式解密消息
            try:
                from wechatpy.enterprise.crypto import WeChatCrypto
                crypto = WeChatCrypto(token, encoding_aes_key, corp_id)
                
                # 解密消息
                decrypted_msg = crypto.decrypt_message(encrypted_msg, msg_signature, timestamp, nonce)
                logger.error(f'消息解密成功，完整内容: {decrypted_msg}')
                
                # 解析XML消息
                try:
                    root = ET.fromstring(decrypted_msg)
                    
                    # 提取所有XML节点信息用于调试
                    xml_info = {}
                    for child in root:
                        xml_info[child.tag] = child.text if child.text else (list(child) if len(child) > 0 else None)
                    logger.info(f'XML解析结果: {xml_info}')
                    
                    msg_type = root.find('MsgType')
                    event = root.find('Event')
                    
                    if msg_type is not None:
                        msg_type_text = msg_type.text
                        logger.error(f'消息类型: {msg_type_text}')
                    else:
                        logger.error('未找到MsgType节点')
                    
                    # 获取事件类型：优先从Event节点获取，如果没有则从InfoType获取
                    event_text = None
                    if event is not None:
                        event_text = event.text
                        logger.error(f'事件类型（从Event节点）: {event_text}')
                    else:
                        logger.error('未找到Event节点，尝试查找其他事件标识')
                        # 尝试查找其他可能的事件标识
                        for child in root:
                            logger.error(f'XML节点: {child.tag} = {child.text}')
                        
                        # 尝试从InfoType获取事件类型
                        info_type = root.find('InfoType')
                        if info_type is not None:
                            event_text = info_type.text
                            logger.info(f'从InfoType获取事件类型: {event_text}')
                    
                    # 处理审批状态通知事件（统一处理，无论event_text从哪里获取）
                    # 企业微信审批事件类型可能是 open_approval_change 或 sys_approval_change
                    logger.error(f'准备判断审批事件，event_text={event_text}, 类型={type(event_text)}')
                    if event_text and ('approval' in event_text.lower() or event_text in ['open_approval_change', 'sys_approval_change']):
                        logger.error(f'检测到审批事件，事件类型: {event_text}')
                        # 根据事件类型确定解析方式
                        parse_event_type = 'sys_approval_change' if event_text == 'sys_approval_change' else 'open_approval_change'
                        logger.error(f'使用解析类型: {parse_event_type}')
                        
                        # 审批状态变化事件
                        try:
                            approval_info = self._parse_approval_event(root, event_type=parse_event_type)
                            logger.error(f'审批状态变化事件解析结果: {approval_info}')
                            
                            # 处理审批事件并发送消息通知
                            logger.error('开始处理审批事件并发送通知...')
                            self._process_approval_event_and_notify(approval_info, logger)
                            logger.error('审批事件处理完成')
                        except Exception as e:
                            logger.error(f'处理审批事件失败: {str(e)}', exc_info=True)
                            # 即使通知失败，也返回success，避免企业微信重复推送
                    else:
                        logger.error(f'非审批事件，事件类型: {event_text}，跳过处理')
                            
                except ET.ParseError as e:
                    logger.error(f'XML解析失败: {str(e)}')
                    logger.error(f'XML内容: {decrypted_msg}')
                except Exception as e:
                    logger.error(f'处理审批事件失败: {str(e)}', exc_info=True)
                
                # 返回success表示成功接收
                return HttpResponse('success', content_type='text/plain')
                
            except ValueError as e:
                logger.error(f'签名验证失败: {str(e)}')
                return HttpResponse('签名验证失败', status=403)
            except Exception as e:
                logger.error(f'解密消息失败: {str(e)}', exc_info=True)
                return HttpResponse(f'解密失败: {str(e)}', status=500)
                
        except Exception as e:
            logger.error(f'处理审批事件时出错: {str(e)}', exc_info=True)
            return HttpResponse(f'服务器错误: {str(e)}', status=500)


def custom_logout(request):
    """自定义登出函数，清除所有session和cookie"""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    
    # 清除所有session数据
    request.session.flush()
    # 清除用户的所有session
    if hasattr(request, 'user'):
        logout(request)

    response = redirect('login')
    # 清除相关的cookie
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')

    return response
    
    def _parse_approval_event(self, root, event_type='sys_approval_change'):
        """
        解析审批事件XML数据
        支持两种事件类型：
        - sys_approval_change: 系统审批变化（实际使用）
        - open_approval_change: 开放平台审批变化
        返回结构化的审批信息字典
        """
        import xml.etree.ElementTree as ET
        
        approval_info = {
            'agent_id': None,
            'approval_info': {},
            'event_type': event_type
        }
        
        # 提取基本信息
        for child in root:
            if child.tag == 'AgentID':
                approval_info['agent_id'] = child.text
            elif child.tag == 'ApprovalInfo':
                # 审批信息
                approval_detail = {}
                
                # 根据事件类型解析不同的XML结构
                if event_type == 'sys_approval_change':
                    # sys_approval_change 事件结构
                    for info_child in child:
                        if info_child.tag == 'SpNo':
                            approval_detail['ThirdNo'] = info_child.text  # 审批单号
                        elif info_child.tag == 'SpName':
                            approval_detail['OpenSpName'] = info_child.text  # 审批模板名称
                        elif info_child.tag == 'SpStatus':
                            approval_detail['OpenSpStatus'] = info_child.text  # 审批状态
                        elif info_child.tag == 'ApplyTime':
                            approval_detail['ApplyTime'] = info_child.text  # 申请时间
                        elif info_child.tag == 'Applyer':
                            # 申请人信息
                            for applyer_child in info_child:
                                if applyer_child.tag == 'UserId':
                                    approval_detail['ApplyUserId'] = applyer_child.text
                                    approval_detail['ApplyUserName'] = applyer_child.text  # 暂时用UserID，后续可以从企业微信API获取姓名
                        elif info_child.tag == 'SpRecord':
                            # 审批记录（审批人信息）
                            if 'approval_nodes' not in approval_detail:
                                approval_detail['approval_nodes'] = []
                            
                            node_info = {}
                            item_info = {}  # 初始化item_info
                            for record_child in info_child:
                                if record_child.tag == 'SpStatus':
                                    node_info['NodeStatus'] = record_child.text
                                elif record_child.tag == 'Details':
                                    # 审批人详情
                                    items = []
                                    for detail_child in record_child:
                                        if detail_child.tag == 'Approver':
                                            # 处理审批人信息
                                            for approver_child in detail_child:
                                                if approver_child.tag == 'UserId':
                                                    item_info = {
                                                        'ItemUserId': approver_child.text,
                                                        'ItemName': approver_child.text  # 暂时用UserID
                                                    }
                                        elif detail_child.tag == 'Speech':
                                            # 审批意见
                                            if item_info:
                                                item_info['ItemSpeech'] = detail_child.text
                                        elif detail_child.tag == 'SpStatus':
                                            # 审批状态
                                            if item_info:
                                                item_info['ItemStatus'] = detail_child.text
                                    
                                    # 如果收集到了审批人信息，添加到列表
                                    if item_info and item_info.get('ItemUserId'):
                                        items.append(item_info)
                                    node_info['items'] = items
                            
                            if node_info:
                                approval_detail['approval_nodes'].append(node_info)
                        else:
                            approval_detail[info_child.tag] = info_child.text
                
                elif event_type == 'open_approval_change':
                    # open_approval_change 事件结构（原有逻辑）
                    for info_child in child:
                        if info_child.tag == 'ApprovalNode':
                            # 审批节点信息
                            nodes = []
                            for node in info_child:
                                node_info = {}
                                for node_child in node:
                                    if node_child.tag == 'Items':
                                        # 审批人列表
                                        items = []
                                        for item in node_child:
                                            item_info = {}
                                            for item_child in item:
                                                item_info[item_child.tag] = item_child.text
                                            items.append(item_info)
                                        node_info['items'] = items
                                    else:
                                        node_info[node_child.tag] = node_child.text
                                nodes.append(node_info)
                            approval_detail['approval_nodes'] = nodes
                        else:
                            approval_detail[info_child.tag] = info_child.text
                
                approval_info['approval_info'] = approval_detail
        
        return approval_info
    
    def _get_wechat_access_token(self, logger):
        """
        获取企业微信access_token
        返回access_token，失败返回None
        """
        try:
            import requests
            
            # 获取企业微信配置
            corp_id = os.environ.get('WECHAT_CORP_ID')
            corp_secret = os.environ.get('WECHAT_APP_SECRET')
            
            if not corp_id or not corp_secret:
                logger.error('缺少企业微信配置')
                return None
            
            # 获取access_token
            token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}'
            token_resp = requests.get(token_url, timeout=10)
            token_data = token_resp.json()
            
            if token_data.get('errcode') != 0:
                logger.error(f'获取access_token失败: {token_data}')
                return None
            
            return token_data.get('access_token')
            
        except Exception as e:
            logger.error(f'获取access_token失败: {str(e)}', exc_info=True)
            return None
    
    def _get_approval_detail(self, sp_no, logger):
        """
        通过审批单号获取审批详情（包含具体审批内容）
        返回审批详情字典，失败返回None
        """
        try:
            import requests
            
            access_token = self._get_wechat_access_token(logger)
            if not access_token:
                return None
            
            # 调用企业微信API获取审批详情
            detail_url = f'https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovaldetail?access_token={access_token}'
            detail_data = {
                "sp_no": sp_no
            }
            
            response = requests.post(detail_url, json=detail_data, timeout=10)
            result = response.json()
            
            if result.get('errcode') != 0:
                logger.error(f'获取审批详情失败: {result}')
                return None
            
            logger.info(f'成功获取审批详情: {sp_no}')
            return result
            
        except Exception as e:
            logger.error(f'获取审批详情失败: {str(e)}', exc_info=True)
            return None
    
    def _extract_title_text(self, title):
        """
        从标题字段中提取中文文本
        title可能是字符串或多语言数组
        """
        if isinstance(title, str):
            return title
        elif isinstance(title, list):
            # 多语言数组，优先提取中文
            for item in title:
                if isinstance(item, dict):
                    lang = item.get('lang', '')
                    text = item.get('text', '')
                    if lang == 'zh_CN' and text:
                        return text
                    elif text and not lang:  # 如果没有lang字段，也使用
                        return text
            # 如果没找到中文，返回第一个有text的
            for item in title:
                if isinstance(item, dict):
                    text = item.get('text', '')
                    if text:
                        return text
        return str(title) if title else ''
    
    def _extract_field_value(self, control, value):
        """
        根据控件类型提取字段的实际值
        返回格式化后的字符串，如果为空或不需要显示则返回None
        """
        from datetime import datetime
        
        # 不显示的控件类型（附件、图片等）
        skip_controls = ['File', 'Image', 'Attach', 'Attachment']
        if control in skip_controls:
            return None
        
        # 如果value为空或None
        if not value:
            return None
        
        # 如果value直接是字符串，且不是附件类型，直接返回
        if isinstance(value, str) and control not in skip_controls:
            return value.strip() if value.strip() else None
        
        # 文本类型控件
        if control in ['Text', 'Textarea', 'TextArea', '']:
            # 如果是字典，提取text字段
            if isinstance(value, dict):
                text = value.get('text', '')
                # 如果text为空，检查是否是空字典（只有空数组字段）
                if not text:
                    # 检查是否有非空的有效字段
                    has_content = any(
                        v for k, v in value.items() 
                        if k not in ['tips', 'members', 'departments', 'files', 'children', 
                                    'stat_field', 'sum_field', 'related_approval', 'students', 
                                    'classes', 'docs', 'wedrive_files'] and v
                    )
                    if not has_content:
                        return None
                return text.strip() if text else None
            return None
        
        # 日期时间类型控件
        if control in ['Date', 'DateTime', 'DateRange']:
            if isinstance(value, dict):
                date_info = value.get('date', {})
                if isinstance(date_info, dict):
                    s_timestamp = date_info.get('s_timestamp', '')
                    if s_timestamp:
                        try:
                            dt = datetime.fromtimestamp(int(s_timestamp))
                            return dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                # 尝试直接获取text字段
                text = value.get('text', '')
                if text:
                    return text
            elif isinstance(value, (str, int)):
                try:
                    dt = datetime.fromtimestamp(int(value))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    return str(value) if value else None
            return None
        
        # 数字类型控件
        if control in ['Number', 'Money']:
            if isinstance(value, dict):
                num = value.get('number', '') or value.get('value', '')
                return str(num) if num else None
            return str(value) if value else None
        
        # 选择类型控件（单选、多选）
        if control in ['Selector', 'MultiSelector', 'Contact', 'Table']:
            if isinstance(value, list):
                text_values = []
                for v in value:
                    if isinstance(v, dict):
                        text = v.get('text', '') or v.get('title', '') or v.get('name', '')
                        if text:
                            text_values.append(str(text))
                    elif isinstance(v, (str, int, float)):
                        text_values.append(str(v))
                return '、'.join(text_values) if text_values else None
            elif isinstance(value, dict):
                text = value.get('text', '') or value.get('title', '') or value.get('name', '')
                return text if text else None
            return str(value) if value else None
        
        # 默认处理：尝试提取文本值
        if isinstance(value, dict):
            # 检查是否是空字典（只有空数组字段）
            # 排除这些常见的空字段
            empty_keys = ['tips', 'members', 'departments', 'files', 'children', 
                         'stat_field', 'sum_field', 'related_approval', 'students', 
                         'classes', 'docs', 'wedrive_files']
            
            has_content = False
            for k, v in value.items():
                if k in empty_keys:
                    continue
                if k in ['text', 'title', 'value', 'number'] and v:
                    has_content = True
                    break
                elif isinstance(v, dict) and v:
                    # 检查嵌套字典是否有内容
                    nested_has_content = any(
                        nv for nk, nv in v.items() 
                        if nk not in empty_keys and nv
                    )
                    if nested_has_content:
                        has_content = True
                        break
                elif isinstance(v, list) and v:
                    has_content = True
                    break
                elif v and k not in empty_keys:
                    has_content = True
                    break
            
            if not has_content:
                return None
            
            # 尝试提取文本
            text = value.get('text', '') or value.get('title', '') or value.get('value', '')
            if text:
                return str(text)
            return None
        elif isinstance(value, list):
            # 列表类型，提取文本值
            text_values = []
            for v in value:
                if isinstance(v, dict):
                    text = v.get('text', '') or v.get('title', '')
                    if text:
                        text_values.append(str(text))
                elif isinstance(v, (str, int, float)) and v:
                    text_values.append(str(v))
            return '、'.join(text_values) if text_values else None
        elif isinstance(value, (str, int, float)):
            return str(value) if value else None
        
        return None
    
    def _format_approval_content(self, approval_detail, logger):
        """
        格式化审批内容，从审批详情中提取具体内容字段
        返回格式化的审批内容字符串
        """
        try:
            if not approval_detail:
                return ""
            
            info = approval_detail.get('info', {})
            apply_data = info.get('apply_data', {})
            
            if not apply_data:
                return ""
            
            content_lines = []
            
            # 遍历apply_data中的字段
            contents = apply_data.get('contents', [])
            for content_item in contents:
                control = content_item.get('control', '')
                title_raw = content_item.get('title', '')
                value = content_item.get('value', [])
                
                # 提取标题文本（中文）
                title_text = self._extract_title_text(title_raw)
                
                # 提取字段值
                value_str = self._extract_field_value(control, value)
                
                # 只显示有值的字段
                if value_str and value_str.strip():
                    content_lines.append(f"  • {title_text}：{value_str}")
            
            # 如果没有有效内容，返回空字符串
            if not content_lines:
                return ""
            
            # 构建完整内容
            result = "📋 审批内容：\n" + "\n".join(content_lines) + "\n"
            return result
            
        except Exception as e:
            logger.error(f'格式化审批内容失败: {str(e)}', exc_info=True)
            return ""
    
    def _send_approval_notification(self, userid, message_content, logger):
        """
        发送审批通知消息给指定用户
        """
        try:
            import requests
            
            # 获取企业微信配置
            corp_id = os.environ.get('WECHAT_CORP_ID')
            corp_secret = os.environ.get('WECHAT_APP_SECRET')
            agent_id = os.environ.get('WECHAT_AGENT_ID', '1000016')
            
            if not corp_id or not corp_secret:
                logger.error('缺少企业微信配置，无法发送消息')
                return False
            
            # 获取access_token
            access_token = self._get_wechat_access_token(logger)
            if not access_token:
                return False
            
            # 发送消息给指定用户
            message_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
            
            message_data = {
                "touser": userid,
                "msgtype": "text",
                "agentid": agent_id,
                "text": {
                    "content": message_content
                }
            }
            
            response = requests.post(message_url, json=message_data, timeout=10)
            result = response.json()
            
            if result.get('errcode') != 0:
                logger.error(f'发送消息给{userid}失败: {result}')
                return False
            
            logger.info(f'成功发送审批通知消息给{userid}')
            return True
            
        except Exception as e:
            logger.error(f'发送审批通知消息给{userid}失败: {str(e)}', exc_info=True)
            return False
    
    def _process_approval_event_and_notify(self, approval_info, logger):
        """
        处理审批事件并发送通知消息给相关用户
        """
        approval_detail = approval_info.get('approval_info', {})
        
        # 提取审批信息
        third_no = approval_detail.get('ThirdNo', '')  # 审批单号
        open_sp_name = approval_detail.get('OpenSpName', '')  # 审批模板名称
        open_sp_status = approval_detail.get('OpenSpStatus', '')  # 审批状态
        apply_user_name = approval_detail.get('ApplyUserName', '')  # 申请人姓名
        apply_user_id = approval_detail.get('ApplyUserId', '')  # 申请人UserID
        apply_time = approval_detail.get('ApplyTime', '')  # 申请时间
        
        # 审批状态映射
        status_map = {
            '1': '审批中',
            '2': '已通过',
            '3': '已驳回',
            '4': '已撤销',
            '6': '已转审'
        }
        status_text = status_map.get(open_sp_status, f'未知状态({open_sp_status})')
        
        # 格式化申请时间
        try:
            from datetime import datetime
            if apply_time:
                apply_time_int = int(apply_time)
                apply_time_str = datetime.fromtimestamp(apply_time_int).strftime('%Y-%m-%d %H:%M:%S')
            else:
                apply_time_str = '未知时间'
        except:
            apply_time_str = apply_time or '未知时间'
        
        # 获取审批详情（包含具体审批内容）
        approval_detail_data = None
        approval_content_text = ""
        if third_no:
            logger.info(f'开始获取审批详情: {third_no}')
            approval_detail_data = self._get_approval_detail(third_no, logger)
            if approval_detail_data:
                approval_content_text = self._format_approval_content(approval_detail_data, logger)
                if approval_content_text:
                    logger.info(f'成功获取并格式化审批内容')
                else:
                    logger.info(f'审批详情中未找到具体内容字段')
            else:
                logger.warning(f'获取审批详情失败，将只发送基本信息')
        
        # 构建消息内容
        message_content = f"""📋 审批状态通知

📝 审批单号：{third_no}
📄 审批模板：{open_sp_name}
👤 申请人：{apply_user_name}
⏰ 申请时间：{apply_time_str}
✅ 审批状态：{status_text}

"""
        
        # 添加审批内容（如果有）
        if approval_content_text:
            message_content += approval_content_text
        
        # 提取审批节点信息，获取审批人
        approval_nodes = approval_detail.get('approval_nodes', [])
        notified_users = set()  # 用于去重
        
        # 通知申请人
        if apply_user_id and apply_user_id not in notified_users:
            logger.info(f'准备通知申请人: {apply_user_id} ({apply_user_name})')
            user_message = message_content + "💡 这是您提交的审批申请。"
            success = self._send_approval_notification(apply_user_id, user_message, logger)
            if success:
                logger.info(f'成功通知申请人: {apply_user_id}')
            else:
                logger.error(f'通知申请人失败: {apply_user_id}')
            notified_users.add(apply_user_id)
        else:
            logger.warning(f'跳过通知申请人，原因: apply_user_id={apply_user_id}, 已在通知列表={apply_user_id in notified_users if apply_user_id else "N/A"}')
        
        # 通知审批人
        for node in approval_nodes:
            node_status = node.get('NodeStatus', '')
            items = node.get('items', [])
            
            for item in items:
                item_user_id = item.get('ItemUserId', '')
                item_user_name = item.get('ItemName', '')
                item_status = item.get('ItemStatus', '')
                item_speech = item.get('ItemSpeech', '')  # 审批意见
                
                if item_user_id and item_user_id not in notified_users:
                    logger.info(f'准备通知审批人: {item_user_id} ({item_user_name}), 节点状态: {node_status}, 审批状态: {item_status}')
                    # 构建审批人专属消息
                    approver_message = message_content
                    
                    # 添加审批意见（如果有）
                    if item_speech:
                        approver_message += f"💬 审批意见：{item_speech}\n\n"
                    
                    # 根据节点状态添加提示
                    if node_status == '1':
                        approver_message += "⏳ 该审批正在等待您的处理。"
                    elif node_status == '2':
                        approver_message += "✅ 您已同意该审批。"
                    elif node_status == '3':
                        approver_message += "❌ 您已驳回该审批。"
                    
                    success = self._send_approval_notification(item_user_id, approver_message, logger)
                    if success:
                        logger.info(f'成功通知审批人: {item_user_id}')
                    else:
                        logger.error(f'通知审批人失败: {item_user_id}')
                    notified_users.add(item_user_id)
        
        logger.info(f'审批事件处理完成，已通知 {len(notified_users)} 位用户')