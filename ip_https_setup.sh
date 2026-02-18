#!/bin/bash

# 🔐 临时IP地址HTTPS配置（不推荐生产环境）
# 注意：浏览器会显示证书警告

echo "🔐 为IP地址配置自签名SSL证书..."

if [[ $EUID -ne 0 ]]; then
   echo "❌ 请使用root权限运行此脚本"
   exit 1
fi

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me)
echo "🌐 服务器IP: $SERVER_IP"

# 创建自签名证书
echo "🔒 创建自签名SSL证书..."
mkdir -p /etc/ssl/certs
mkdir -p /etc/ssl/private

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -subj "/C=CN/ST=Jilin/L=Changchun/O=YuanTong/CN=$SERVER_IP"

# 创建Nginx配置
cat > /etc/nginx/sites-available/yuantong-ip << EOF
server {
    listen 80;
    server_name $SERVER_IP;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name $SERVER_IP;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

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

# 启用配置
rm -f /etc/nginx/sites-enabled/*
ln -sf /etc/nginx/sites-available/yuantong-ip /etc/nginx/sites-enabled/

# 重启Nginx
nginx -t && systemctl restart nginx

echo "✅ 配置完成！"
echo "🌐 访问地址: https://$SERVER_IP"
echo "⚠️  注意：浏览器会显示安全警告，点击'高级' -> '继续访问'即可" 