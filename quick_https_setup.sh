#!/bin/bash

# 🔐 吉林远通 - 快速HTTPS设置脚本
# 适合初学者使用的简化版本

echo "🔐 开始为 jilinyuantong.top 配置免费HTTPS..."

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   echo "❌ 请使用root权限运行此脚本"
   echo "💡 使用命令: sudo $0"
   exit 1
fi

# 获取用户输入
echo "📝 请提供以下信息："
read -p "🌐 请输入你的域名 (例: jilinyuantong.top): " DOMAIN
read -p "📧 请输入你的邮箱 (用于SSL证书通知): " EMAIL

if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
    echo "❌ 域名和邮箱不能为空"
    exit 1
fi

echo "✅ 配置信息确认："
echo "   域名: $DOMAIN"
echo "   邮箱: $EMAIL"

read -p "🤔 确认信息正确吗? (y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ 用户取消操作"
    exit 1
fi

echo ""
echo "🚀 开始自动配置..."

# 步骤1: 检测系统类型并安装必要软件
echo "📦 检测系统类型并安装必要软件..."

# 检测系统类型
if [[ -f /etc/debian_version ]]; then
    # Ubuntu/Debian
    echo "   检测到 Ubuntu/Debian 系统"
    apt update -qq
    apt install -y nginx certbot python3-certbot-nginx ufw curl dnsutils > /dev/null 2>&1
    FIREWALL_CMD="ufw"
elif [[ -f /etc/redhat-release ]]; then
    # CentOS/RHEL
    echo "   检测到 CentOS/RHEL 系统"
    yum update -y -q > /dev/null 2>&1
    yum install -y epel-release > /dev/null 2>&1
    yum install -y nginx firewalld curl bind-utils > /dev/null 2>&1
    
    # 安装certbot和nginx插件
    yum install -y python3-certbot-nginx > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        # 如果python3-certbot-nginx不可用，尝试其他方式安装
        yum install -y certbot > /dev/null 2>&1
        pip3 install certbot-nginx > /dev/null 2>&1
    fi
    
    FIREWALL_CMD="firewalld"
else
    echo "❌ 不支持的操作系统"
    echo "💡 支持的系统：Ubuntu, Debian, CentOS, RHEL"
    exit 1
fi

if [[ $? -eq 0 ]]; then
    echo "✅ 软件安装完成"
else
    echo "❌ 软件安装失败"
    exit 1
fi

# 步骤2: 配置防火墙
echo "🔥 配置防火墙..."

if [[ "$FIREWALL_CMD" == "ufw" ]]; then
    # Ubuntu/Debian - UFW
    ufw --force enable > /dev/null 2>&1
    ufw allow ssh > /dev/null 2>&1
    ufw allow 80 > /dev/null 2>&1
    ufw allow 443 > /dev/null 2>&1
elif [[ "$FIREWALL_CMD" == "firewalld" ]]; then
    # CentOS/RHEL - firewalld
    systemctl enable firewalld > /dev/null 2>&1
    systemctl start firewalld > /dev/null 2>&1
    firewall-cmd --permanent --add-service=ssh > /dev/null 2>&1
    firewall-cmd --permanent --add-service=http > /dev/null 2>&1
    firewall-cmd --permanent --add-service=https > /dev/null 2>&1
    firewall-cmd --reload > /dev/null 2>&1
fi

echo "✅ 防火墙配置完成"

# 启动并启用Nginx服务
echo "🚀 启动Nginx服务..."
systemctl enable nginx > /dev/null 2>&1
systemctl start nginx > /dev/null 2>&1

# 步骤3: 检查域名解析
echo "🔍 检查域名解析..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

echo "   服务器IP: $SERVER_IP"
echo "   域名解析IP: $DOMAIN_IP"

if [[ "$DOMAIN_IP" != "$SERVER_IP" ]]; then
    echo "⚠️  警告: 域名解析可能不正确"
    echo "   请确保域名 $DOMAIN 已正确解析到服务器 $SERVER_IP"
    read -p "🤔 是否继续? (y/n): " continue_setup
    if [[ ! $continue_setup =~ ^[Yy]$ ]]; then
        echo "❌ 请先配置正确的域名解析"
        exit 1
    fi
fi

# 步骤4: 创建临时Nginx配置
echo "⚙️  创建Nginx配置..."

# 创建sites-available和sites-enabled目录（CentOS可能没有）
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# 确保nginx.conf包含sites-enabled目录
if ! grep -q "sites-enabled" /etc/nginx/nginx.conf; then
    sed -i '/http {/a\    include /etc/nginx/sites-enabled/*;' /etc/nginx/nginx.conf
fi

cat > /etc/nginx/sites-available/yuantong-temp << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 200 "正在配置HTTPS，请稍候...";
        add_header Content-Type text/plain;
    }
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/yuantong-temp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 创建web根目录
mkdir -p /var/www/html

# 测试并启动Nginx
nginx -t > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    systemctl restart nginx
    echo "✅ Nginx配置完成"
else
    echo "❌ Nginx配置错误"
    echo "💡 查看错误详情："
    nginx -t
    exit 1
fi

# 步骤5: 申请SSL证书
echo "🔒 申请Let's Encrypt SSL证书..."
echo "   这可能需要几分钟时间..."

certbot --nginx \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo "✅ SSL证书申请成功"
else
    echo "❌ SSL证书申请失败"
    echo "💡 可能的原因："
    echo "   1. 域名解析不正确"
    echo "   2. 防火墙阻止了80端口"
    echo "   3. 已达到申请频率限制"
    echo ""
    echo "🔧 查看详细错误信息："
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --no-eff-email
    exit 1
fi

# 步骤6: 创建生产环境Nginx配置
echo "🏭 创建生产环境配置..."
cat > /etc/nginx/sites-available/yuantong << EOF
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
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
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
EOF

# 启用生产配置
rm -f /etc/nginx/sites-enabled/yuantong-temp
ln -sf /etc/nginx/sites-available/yuantong /etc/nginx/sites-enabled/

# 测试配置
nginx -t > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    systemctl restart nginx
    echo "✅ 生产环境配置完成"
else
    echo "❌ 生产环境配置错误"
    echo "💡 查看错误详情："
    nginx -t
    exit 1
fi

# 步骤7: 设置自动续期
echo "🔄 设置SSL证书自动续期..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -
echo "✅ 自动续期设置完成"

# 步骤8: 验证HTTPS
echo "🔍 验证HTTPS配置..."
sleep 3

# 检查HTTP重定向
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" 2>/dev/null || echo "000")
if [[ "$HTTP_STATUS" == "301" || "$HTTP_STATUS" == "302" ]]; then
    echo "✅ HTTP重定向正常"
else
    echo "⚠️  HTTP重定向可能有问题 (状态码: $HTTP_STATUS)"
fi

# 检查HTTPS访问
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" 2>/dev/null || echo "000")
if [[ "$HTTPS_STATUS" == "200" || "$HTTPS_STATUS" == "502" ]]; then
    echo "✅ HTTPS访问正常"
else
    echo "⚠️  HTTPS访问可能有问题 (状态码: $HTTPS_STATUS)"
fi

# 显示结果
echo ""
echo "🎉 HTTPS配置完成！"
echo ""
echo "📋 配置信息："
echo "   🌐 域名: $DOMAIN"
echo "   🔒 HTTPS地址: https://$DOMAIN"
echo "   📧 通知邮箱: $EMAIL"
echo "   📁 证书路径: /etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "🔧 管理命令："
echo "   查看证书状态: sudo certbot certificates"
echo "   手动续期: sudo certbot renew"
echo "   重启Nginx: sudo systemctl restart nginx"
echo "   查看Nginx状态: sudo systemctl status nginx"
echo ""
echo "🌐 访问地址："
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
echo "📝 下一步："
echo "   1. 确保Django应用正在运行在8000端口"
echo "   2. 更新.env文件中的HTTPS配置"
echo "   3. 重启Django应用"
echo ""
echo "💡 提示："
echo "   - SSL证书有效期90天，已设置自动续期"
echo "   - 可以访问 https://www.ssllabs.com/ssltest/ 测试SSL安全评级"
echo ""
echo "✅ 部署完成！享受你的HTTPS网站吧！🎊" 