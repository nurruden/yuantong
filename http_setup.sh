#!/bin/bash

# 🌐 HTTP配置脚本 - 等待域名解析后再配置HTTPS

echo "🌐 配置HTTP访问..."

if [[ $EUID -ne 0 ]]; then
   echo "❌ 请使用root权限运行此脚本"
   exit 1
fi

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me)
echo "🌐 服务器IP: $SERVER_IP"

# 创建HTTP Nginx配置
cat > /etc/nginx/sites-available/yuantong-http << EOF
server {
    listen 80;
    server_name jilinyuantong.top www.jilinyuantong.top $SERVER_IP;

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
ln -sf /etc/nginx/sites-available/yuantong-http /etc/nginx/sites-enabled/

# 重启Nginx
nginx -t && systemctl restart nginx

echo "✅ HTTP配置完成！"
echo ""
echo "🌐 当前可用访问方式："
echo "   http://$SERVER_IP"
echo "   http://jilinyuantong.top (需要域名解析)"
echo ""
echo "📋 配置域名解析后："
echo "   1. 在域名管理面板添加A记录："
echo "      类型: A, 主机记录: @, 记录值: $SERVER_IP"
echo "      类型: A, 主机记录: www, 记录值: $SERVER_IP"
echo "   2. 等待解析生效（通常5-10分钟）"
echo "   3. 运行: sudo ./quick_https_setup.sh"
echo ""
echo "💡 临时可以直接用IP访问: http://$SERVER_IP" 