#!/bin/bash

# 生产环境部署脚本
# 使用方法: sudo ./deploy_production.sh

set -e

PROJECT_DIR="/var/www/yuantong"
NGINX_SITE="yuantong"

echo "🚀 开始部署生产环境..."

# 1. 运行安全配置脚本
echo "🛡️ 运行安全配置..."
if [ -f "$PROJECT_DIR/production_security_setup.sh" ]; then
    chmod +x "$PROJECT_DIR/production_security_setup.sh"
    "$PROJECT_DIR/production_security_setup.sh"
else
    echo "警告: 未找到安全配置脚本"
fi

# 2. 安装Python依赖
echo "📦 安装Python依赖..."
cd "$PROJECT_DIR"
source venv/bin/activate
pip install django-redis redis gunicorn

# 3. 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 4. 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python manage.py migrate

# 5. 创建日志目录
echo "📋 创建日志目录..."
mkdir -p "$PROJECT_DIR/logs"
touch "$PROJECT_DIR/logs/gunicorn_access.log"
touch "$PROJECT_DIR/logs/gunicorn_error.log"
chown -R www-data:www-data "$PROJECT_DIR/logs"

# 6. 设置文件权限
echo "🔒 设置文件权限..."
chown -R www-data:www-data "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
chmod 640 "$PROJECT_DIR/.env.production"

# 7. 安装Gunicorn系统服务
echo "⚙️ 配置Gunicorn服务..."
cp "$PROJECT_DIR/gunicorn_yuantong.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable gunicorn-yuantong
systemctl start gunicorn-yuantong

# 8. 配置Nginx
echo "🌐 配置Nginx..."
cp "$PROJECT_DIR/nginx_yuantong_production.conf" "/etc/nginx/sites-available/$NGINX_SITE"
ln -sf "/etc/nginx/sites-available/$NGINX_SITE" "/etc/nginx/sites-enabled/"

# 删除默认站点
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx

# 9. 创建robots.txt
echo "🤖 创建robots.txt..."
mkdir -p "$PROJECT_DIR/static"
cat > "$PROJECT_DIR/static/robots.txt" << 'EOF'
User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /login/
Disallow: /logout/
Allow: /

Sitemap: https://jilinyuantong.top/sitemap.xml
EOF

# 10. 创建健康检查脚本
echo "🏥 创建健康检查..."
cat > /usr/local/bin/health_check_yuantong.sh << 'EOF'
#!/bin/bash
# 健康检查脚本

HEALTH_URL="https://jilinyuantong.top/health/"
LOGFILE="/var/log/yuantong_health.log"

if curl -f -s "$HEALTH_URL" > /dev/null; then
    echo "$(date): 健康检查通过" >> "$LOGFILE"
    exit 0
else
    echo "$(date): 健康检查失败" >> "$LOGFILE"
    # 重启服务
    systemctl restart gunicorn-yuantong
    exit 1
fi
EOF

chmod +x /usr/local/bin/health_check_yuantong.sh

# 11. 添加健康检查到cron
echo "⏰ 设置健康检查定时任务..."
crontab -l 2>/dev/null | { cat; echo "*/10 * * * * /usr/local/bin/health_check_yuantong.sh"; } | crontab -

# 12. 创建部署后的测试脚本
echo "🧪 创建测试脚本..."
cat > /usr/local/bin/test_yuantong_deployment.sh << 'EOF'
#!/bin/bash
# 部署测试脚本

echo "测试部署状态..."

# 测试服务状态
echo "1. 检查服务状态:"
systemctl is-active gunicorn-yuantong && echo "✅ Gunicorn服务正常" || echo "❌ Gunicorn服务异常"
systemctl is-active nginx && echo "✅ Nginx服务正常" || echo "❌ Nginx服务异常"
systemctl is-active redis-server && echo "✅ Redis服务正常" || echo "❌ Redis服务异常"

# 测试网站可访问性
echo "2. 检查网站可访问性:"
if curl -f -s https://jilinyuantong.top/ > /dev/null; then
    echo "✅ 网站可访问"
else
    echo "❌ 网站不可访问"
fi

# 测试SSL证书
echo "3. 检查SSL证书:"
SSL_DAYS=$(curl -s https://jilinyuantong.top/ --connect-timeout 10 | openssl s_client -servername jilinyuantong.top -connect jilinyuantong.top:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
if [ ! -z "$SSL_DAYS" ]; then
    echo "✅ SSL证书有效: $SSL_DAYS"
else
    echo "❌ SSL证书检查失败"
fi

# 测试数据库连接
echo "4. 检查数据库连接:"
cd /var/www/yuantong
source venv/bin/activate
if python manage.py check --database default; then
    echo "✅ 数据库连接正常"
else
    echo "❌ 数据库连接异常"
fi

echo "测试完成!"
EOF

chmod +x /usr/local/bin/test_yuantong_deployment.sh

# 13. 运行部署测试
echo "🧪 运行部署测试..."
/usr/local/bin/test_yuantong_deployment.sh

echo "✅ 生产环境部署完成！"
echo ""
echo "📋 部署后检查清单:"
echo "1. 修改 /var/www/yuantong/.env.production 中的密码和密钥"
echo "2. 配置邮件服务器设置"
echo "3. 检查防火墙状态: ufw status"
echo "4. 检查SSL证书: certbot certificates"
echo "5. 监控日志: tail -f /var/log/yuantong_monitor.log"
echo "6. 访问网站: https://jilinyuantong.top"
echo ""
echo "📊 系统监控命令:"
echo "- 查看服务状态: systemctl status gunicorn-yuantong"
echo "- 查看应用日志: tail -f /var/www/yuantong/logs/gunicorn_error.log"
echo "- 查看访问日志: tail -f /var/log/nginx/yuantong_access.log"
echo "- 运行健康检查: /usr/local/bin/health_check_yuantong.sh"
echo "- 运行部署测试: /usr/local/bin/test_yuantong_deployment.sh" 