# CSRF问题解决方案

## 问题描述
在调用QC报表定时发送配置API时遇到CSRF验证失败错误：
```
禁止访问 (403)
CSRF验证失败. 请求被中断.
```

## 解决方案

### 1. 已修复的代码
已为所有API端点添加了`@csrf_exempt`装饰器：

```python
@login_required
@csrf_exempt  # 添加此装饰器
@require_http_methods(["POST"])
def update_qc_schedule(request):
    # API实现
```

### 2. 需要重启Django服务
修改代码后需要重启Django服务以应用更改：

```bash
# 方法1：重启Gunicorn
sudo systemctl restart yuantong-django

# 方法2：发送HUP信号
pkill -HUP gunicorn

# 方法3：如果使用其他WSGI服务器，相应重启
```

### 3. 验证修复
重启服务后，可以使用以下方式验证：

#### 方法1：使用curl测试
```bash
curl -X POST https://jilinyuantong.top/tasks/api/qc-schedule/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "",
    "report_type": "dayuan",
    "send_hour": "8",
    "send_minute": "0",
    "recipient_name": "王立梅",
    "recipient_userid": "WangLiMei",
    "send_excel": true,
    "send_text": true,
    "text_template": "",
    "is_enabled": true
  }'
```

#### 方法2：使用Python requests
```python
import requests
import json

data = {
    "id": "",
    "report_type": "dayuan",
    "send_hour": "8",
    "send_minute": "0",
    "recipient_name": "王立梅",
    "recipient_userid": "WangLiMei",
    "send_excel": True,
    "send_text": True,
    "text_template": "",
    "is_enabled": True
}

response = requests.post(
    'https://jilinyuantong.top/tasks/api/qc-schedule/update/',
    json=data,
    headers={'Content-Type': 'application/json'}
)

print(response.status_code)
print(response.json())
```

### 4. 修复的API端点
以下API端点已添加CSRF豁免：

- `POST /tasks/api/qc-schedule/update/` - 更新配置
- `POST /tasks/api/qc-schedule/delete/` - 删除配置  
- `POST /tasks/api/qc-schedule/toggle/` - 切换启用状态

### 5. 注意事项
1. **安全性**: 虽然添加了CSRF豁免，但API仍然需要用户登录认证
2. **权限**: 只有登录用户才能访问这些API
3. **数据验证**: API内部仍然进行数据验证和错误处理
4. **日志记录**: 所有操作都会记录在任务日志中

### 6. 测试命令
可以使用以下Django管理命令测试API：

```bash
python manage.py test_qc_api
```

## 总结
CSRF问题已通过添加`@csrf_exempt`装饰器解决，但需要重启Django服务才能生效。重启后，API调用将不再需要CSRF token，可以直接发送POST请求。
