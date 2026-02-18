# 🛡️ 华为云部署安全指南 - jilinyuantong.top

## 🔒 安全修复完成

已完成以下安全加固措施：

### 1. 敏感信息保护
- ✅ 移除所有硬编码的密钥、密码和API密钥
- ✅ 使用环境变量管理敏感配置
- ✅ 删除不安全的配置文件 `config/wechat_config.py`

### 2. 生产环境安全配置
- ✅ 强制HTTPS重定向
- ✅ 启用HSTS安全头
- ✅ 防止XSS和内容类型嗅探
- ✅ 严格的Session和CSRF配置
- ✅ 增强密码验证规则（生产环境最少12位）

### 3. 数据库安全
- ✅ 使用环境变量配置数据库连接
- ✅ 设置安全的字符集和SQL模式

## 🚀 部署前准备

### 1. 在华为云服务器上创建环境变量文件

```bash
# 在服务器上创建 .env 文件
sudo nano /path/to/your/project/.env
```

复制以下内容并修改为你的实际配置：

```bash
# Django 配置
SECRET_KEY=2zezo@%a^h@%hwe8piu#)zas55)d#@w&*sjy#v&f#m4(d(v(8*
DEBUG=False
ALLOWED_HOSTS=jilinyuantong.top,www.jilinyuantong.top

# 数据库配置
DB_NAME=yuantong
DB_USER=your_secure_db_user
DB_PASSWORD=your_very_secure_db_password_123!@#
DB_HOST=localhost
DB_PORT=3306

# 微信企业号配置
WECHAT_CORP_ID=ww3579e18459d4e719
WECHAT_APP_SECRET=tj-a2zCrfSrCSFwRN-KJ9E3eRoa4BMybooBzxOXkPE4
WECHAT_CONTACT_SECRET=your_contact_secret
WECHAT_AGENT_ID=1000016
REDIRECT_URI=https://jilinyuantong.top/

# EAS API 配置
EAS_API_HOST=http://139.9.135.148:8081
EAS_API_PATH_ADD=/geteasdata/addManufactureRec
EAS_API_PATH_UPDATE=/geteasdata/upManufactureRec
EAS_API_PATH_DELETE=/geteasdata/delManufactureRec
EAS_API_PATH_GET=/geteasdata/getManufactureRec

# 安全配置
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
```

## 🔐 免费SSL证书申请和配置

### 方法一：使用 Let's Encrypt + Certbot（推荐）

Let's Encrypt 是最受欢迎的免费SSL证书提供商，证书有效期90天，可自动续期。

#### 1. 安装 Certbot

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install certbot python3-certbot-nginx
```

#### 2. 申请SSL证书

```bash
# 为你的域名申请证书
sudo certbot --nginx -d jilinyuantong.top -d www.jilinyuantong.top

# 或者只为主域名申请
sudo certbot --nginx -d jilinyuantong.top
```

#### 3. 设置自动续期

```bash
# 测试自动续期
sudo certbot renew --dry-run

# 添加到定时任务
sudo crontab -e
# 添加以下行（每天检查一次）
0 12 * * * /usr/bin/certbot renew --quiet
```

### 方法二：使用华为云SSL证书服务

华为云也提供免费的SSL证书（DV证书），有效期1年：

1. 登录华为云控制台
2. 搜索"SSL证书管理"
3. 点击"购买证书"
4. 选择"DV域名型" → "免费版"
5. 填写域名 `jilinyuantong.top`
6. 完成域名验证
7. 下载证书文件

### 方法三：使用阿里云/腾讯云免费证书

这些云服务商也提供免费的DV证书：

**阿里云：**
- 进入SSL证书服务
- 选择"免费证书"
- 申请并验证域名

**腾讯云：**
- 进入SSL证书管理
- 选择"免费证书"
- 申请并验证域名

## 🔧 Nginx配置（已配置SSL）

创建 `/etc/nginx/sites-available/yuantong` 文件：

```nginx
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name jilinyuantong.top www.jilinyuantong.top;
    return 301 https://$server_name$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name jilinyuantong.top www.jilinyuantong.top;

    # SSL证书配置（Let's Encrypt自动配置）
    ssl_certificate /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jilinyuantong.top/privkey.pem;
    
    # 如果使用其他证书，修改为你的证书路径
    # ssl_certificate /path/to/your/certificate.crt;
    # ssl_certificate_key /path/to/your/private.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    # 静态文件
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
    }
}
```

### 启用Nginx配置

```bash
# 创建软链接启用站点
sudo ln -s /etc/nginx/sites-available/yuantong /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## 🌐 域名解析配置

确保你的域名 `jilinyuantong.top` 已正确解析到华为云服务器：

1. **A记录**：`jilinyuantong.top` → 你的服务器IP
2. **CNAME记录**：`www.jilinyuantong.top` → `jilinyuantong.top`

或者两个都设置为A记录指向服务器IP。

## 🚀 启动服务

### 1. 收集静态文件

```bash
python manage.py collectstatic --noinput
```

### 2. 数据库迁移

```bash
python manage.py migrate
```

### 3. 使用Gunicorn启动

```bash
# 创建Gunicorn配置文件
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# 启动服务
gunicorn --config gunicorn.conf.py yuantong.wsgi:application
```

### 4. 创建系统服务

```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/yuantong.service
```

```ini
[Unit]
Description=Yuantong Django Application
After=network.target

[Service]
User=your-user
Group=your-group
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/venv/bin
EnvironmentFile=/path/to/your/project/.env
ExecStart=/path/to/your/venv/bin/gunicorn --config gunicorn.conf.py yuantong.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable yuantong
sudo systemctl start yuantong
```

## 🔍 SSL证书验证

部署完成后，可以通过以下方式验证SSL证书：

1. **浏览器访问**：https://jilinyuantong.top
2. **在线工具**：https://www.ssllabs.com/ssltest/
3. **命令行检查**：
   ```bash
   openssl s_client -connect jilinyuantong.top:443 -servername jilinyuantong.top
   ```

## ⚠️ 重要提醒

1. **域名解析**：确保域名已正确解析到服务器IP
2. **防火墙**：开放80和443端口
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   ```
3. **证书续期**：Let's Encrypt证书90天有效期，需设置自动续期
4. **备份证书**：定期备份SSL证书文件

## 🎯 部署步骤总结

1. ✅ 配置域名解析
2. ✅ 申请SSL证书（推荐Let's Encrypt）
3. ✅ 配置Nginx
4. ✅ 设置环境变量
5. ✅ 启动Django应用
6. ✅ 验证HTTPS访问

完成这些步骤后，你的网站将通过 https://jilinyuantong.top 安全访问！ 