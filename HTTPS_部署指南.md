# 🔐 免费HTTPS部署指南 - 吉林远通生产管理系统

## 🎯 方案选择：Let's Encrypt（推荐）

Let's Encrypt是最受欢迎的免费SSL证书提供商，具有以下优势：
- ✅ 完全免费
- ✅ 自动续期（90天有效期）
- ✅ 被所有主流浏览器信任
- ✅ 配置简单

## 📋 部署前准备

### 1. 确保域名解析正确
确保你的域名 `jilinyuantong.top` 已经解析到你的华为云服务器IP地址。

**检查方法：**
```bash
# 查看域名解析
nslookup jilinyuantong.top

# 查看服务器IP
curl ifconfig.me
```

### 2. 确保防火墙开放端口
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🚀 一键部署HTTPS（推荐）

我已经为你准备了自动化部署脚本，只需要运行：

```bash
# 给脚本执行权限
chmod +x deploy_https.sh

# 运行部署脚本
sudo ./deploy_https.sh
```

脚本会自动完成：
1. 安装必要软件（Nginx、Certbot）
2. 申请Let's Encrypt SSL证书
3. 配置Nginx HTTPS
4. 设置自动续期
5. 配置安全头

## 🔧 手动部署步骤（备选方案）

如果你想了解详细过程，可以手动执行以下步骤：

### 步骤1：安装Certbot

**Ubuntu/Debian：**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

**CentOS/RHEL：**
```bash
sudo yum install epel-release -y
sudo yum install certbot python3-certbot-nginx -y
```

### 步骤2：申请SSL证书

```bash
# 为你的域名申请证书
sudo certbot --nginx -d jilinyuantong.top -d www.jilinyuantong.top

# 按提示输入邮箱地址
# 同意服务条款
# 选择是否接收邮件通知
```

### 步骤3：验证证书

```bash
# 查看证书状态
sudo certbot certificates

# 测试自动续期
sudo certbot renew --dry-run
```

### 步骤4：配置自动续期

```bash
# 添加定时任务
sudo crontab -e

# 添加以下行（每天中午12点检查续期）
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

## 🛠️ Nginx配置优化

如果需要手动配置Nginx，创建 `/etc/nginx/sites-available/yuantong` 文件：

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

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jilinyuantong.top/privkey.pem;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;

    # 静态文件
    location /static/ {
        alias /var/www/yuantong/staticfiles/;
        expires 1y;
    }

    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/yuantong /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## ⚙️ Django HTTPS配置

更新你的 `.env` 文件：

```bash
# Django 配置
DEBUG=False
ALLOWED_HOSTS=jilinyuantong.top,www.jilinyuantong.top

# 微信企业号配置
REDIRECT_URI=https://jilinyuantong.top/

# HTTPS安全配置
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
```

重启Django应用：
```bash
# 如果使用systemd服务
sudo systemctl restart yuantong

# 或者手动重启
pkill gunicorn
cd /var/www/yuantong
source venv/bin/activate
gunicorn --config gunicorn.conf.py yuantong.wsgi:application &
```

## ✅ 验证HTTPS配置

### 1. 浏览器测试
访问 https://jilinyuantong.top，检查：
- 🔒 地址栏显示锁图标
- ✅ 证书有效
- ✅ 页面正常加载

### 2. 命令行测试
```bash
# 检查HTTP重定向
curl -I http://jilinyuantong.top

# 检查HTTPS访问
curl -I https://jilinyuantong.top

# 检查SSL证书
echo | openssl s_client -servername jilinyuantong.top -connect jilinyuantong.top:443
```

### 3. 在线SSL测试
访问 https://www.ssllabs.com/ssltest/ 输入你的域名进行专业的SSL安全评级测试。

## 🔄 证书管理

### 查看证书状态
```bash
sudo certbot certificates
```

### 手动续期证书
```bash
sudo certbot renew
```

### 强制续期证书
```bash
sudo certbot renew --force-renewal
```

## 🚨 常见问题解决

### 问题1：域名解析错误
```bash
# 检查域名解析
dig jilinyuantong.top
nslookup jilinyuantong.top

# 如果解析不正确，需要在域名注册商处设置A记录
```

### 问题2：防火墙阻止
```bash
# 检查防火墙状态
sudo ufw status
sudo firewall-cmd --list-all

# 开放必要端口
sudo ufw allow 80
sudo ufw allow 443
```

### 问题3：Nginx配置错误
```bash
# 测试Nginx配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 问题4：证书申请失败
```bash
# 查看Certbot日志
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# 常见原因：
# 1. 域名解析不正确
# 2. 防火墙阻止80端口
# 3. Nginx配置错误
# 4. 已达到申请频率限制
```

## 💡 最佳实践建议

1. **定期备份证书**
   ```bash
   sudo cp -r /etc/letsencrypt /backup/letsencrypt-$(date +%Y%m%d)
   ```

2. **监控证书到期**
   ```bash
   # 创建检查脚本
   #!/bin/bash
   certbot certificates | grep "VALID"
   ```

3. **使用强密码**
   - 数据库密码至少12位
   - Django SECRET_KEY使用随机字符串

4. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
   sudo yum update -y  # CentOS/RHEL
   ```

## 🎉 部署完成

成功配置HTTPS后，你的网站将：
- ✅ 通过 https://jilinyuantong.top 安全访问
- ✅ 自动将HTTP请求重定向到HTTPS
- ✅ 获得A+级SSL安全评级
- ✅ 支持HTTP/2协议
- ✅ 证书自动续期

**访问地址：**
- https://jilinyuantong.top
- https://www.jilinyuantong.top

恭喜！你的网站现在已经启用了免费的HTTPS加密！🎊 