#!/bin/bash

# 🔐 吉林远通生产管理系统 HTTPS 部署脚本
# 使用 Let's Encrypt 免费SSL证书

set -e  # 遇到错误立即退出

echo "🔐 开始配置HTTPS..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "此脚本需要root权限运行"
        print_info "请使用: sudo $0"
        exit 1
    fi
}

# 获取用户输入
get_user_input() {
    print_step "收集部署信息..."
    
    # 域名
    read -p "请输入你的域名 (例: jilinyuantong.top): " DOMAIN_NAME
    if [[ -z "$DOMAIN_NAME" ]]; then
        print_error "域名不能为空"
        exit 1
    fi
    
    # 邮箱
    read -p "请输入邮箱地址 (用于SSL证书通知): " EMAIL
    if [[ -z "$EMAIL" ]]; then
        print_error "邮箱不能为空"
        exit 1
    fi
    
    # 项目路径
    read -p "请输入项目路径 (默认: /var/www/yuantong): " PROJECT_PATH
    PROJECT_PATH=${PROJECT_PATH:-/var/www/yuantong}
    
    print_info "配置信息："
    print_info "  域名: $DOMAIN_NAME"
    print_info "  邮箱: $EMAIL"
    print_info "  项目路径: $PROJECT_PATH"
    
    read -p "确认以上信息正确吗? (y/n): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_error "用户取消操作"
        exit 1
    fi
}

# 检查域名解析
check_domain_resolution() {
    print_step "检查域名解析..."
    
    # 获取服务器公网IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || curl -s icanhazip.com)
    
    if [[ -z "$SERVER_IP" ]]; then
        print_warning "无法获取服务器公网IP，请手动检查域名解析"
        return
    fi
    
    print_info "服务器公网IP: $SERVER_IP"
    
    # 检查域名解析
    DOMAIN_IP=$(dig +short $DOMAIN_NAME | tail -n1)
    
    if [[ "$DOMAIN_IP" == "$SERVER_IP" ]]; then
        print_info "✅ 域名解析正确"
    else
        print_warning "⚠️  域名解析可能不正确"
        print_warning "   域名解析IP: $DOMAIN_IP"
        print_warning "   服务器IP: $SERVER_IP"
        print_warning "   请确保域名已正确解析到此服务器"
        
        read -p "是否继续部署? (y/n): " continue_deploy
        if [[ ! $continue_deploy =~ ^[Yy]$ ]]; then
            print_error "请先配置正确的域名解析"
            exit 1
        fi
    fi
}

# 更新系统并安装依赖
install_dependencies() {
    print_step "安装必要的软件包..."
    
    # 检测系统类型
    if [[ -f /etc/debian_version ]]; then
        # Ubuntu/Debian
        apt update
        apt install -y nginx certbot python3-certbot-nginx ufw curl
    elif [[ -f /etc/redhat-release ]]; then
        # CentOS/RHEL
        yum update -y
        yum install -y epel-release
        yum install -y nginx certbot python3-certbot-nginx firewalld curl
    else
        print_error "不支持的操作系统"
        exit 1
    fi
    
    print_info "软件包安装完成"
}

# 配置防火墙
setup_firewall() {
    print_step "配置防火墙..."
    
    if command -v ufw >/dev/null 2>&1; then
        # Ubuntu/Debian - UFW
        ufw --force enable
        ufw allow ssh
        ufw allow 80/tcp
        ufw allow 443/tcp
        print_info "UFW防火墙配置完成"
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # CentOS/RHEL - firewalld
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        print_info "firewalld防火墙配置完成"
    else
        print_warning "未检测到防火墙，请手动开放80和443端口"
    fi
}

# 创建临时Nginx配置（用于证书验证）
create_temp_nginx_config() {
    print_step "创建临时Nginx配置..."
    
    cat > /etc/nginx/sites-available/yuantong-temp << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    # 启用临时配置
    ln -sf /etc/nginx/sites-available/yuantong-temp /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试并重启Nginx
    nginx -t
    systemctl restart nginx
    
    print_info "临时Nginx配置创建完成"
}

# 申请SSL证书
obtain_ssl_certificate() {
    print_step "申请Let's Encrypt SSL证书..."
    
    # 申请证书
    certbot --nginx \
        -d "$DOMAIN_NAME" \
        -d "www.$DOMAIN_NAME" \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --non-interactive
    
    if [[ $? -eq 0 ]]; then
        print_info "✅ SSL证书申请成功"
    else
        print_error "❌ SSL证书申请失败"
        print_error "请检查："
        print_error "1. 域名是否正确解析到此服务器"
        print_error "2. 防火墙是否开放80和443端口"
        print_error "3. Nginx是否正常运行"
        exit 1
    fi
}

# 创建生产环境Nginx配置
create_production_nginx_config() {
    print_step "创建生产环境Nginx配置..."
    
    cat > /etc/nginx/sites-available/yuantong << EOF
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA256:DHE-RSA-AES256-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://res.wx.qq.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;" always;

    # 客户端最大上传大小
    client_max_body_size 100M;

    # 静态文件
    location /static/ {
        alias $PROJECT_PATH/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # 静态文件压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/css text/javascript application/javascript application/json;
    }

    # 媒体文件
    location /media/ {
        alias $PROJECT_PATH/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_redirect off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # 启用生产配置
    rm -f /etc/nginx/sites-enabled/yuantong-temp
    ln -sf /etc/nginx/sites-available/yuantong /etc/nginx/sites-enabled/
    
    # 测试配置
    nginx -t
    
    print_info "生产环境Nginx配置创建完成"
}

# 设置SSL证书自动续期
setup_ssl_auto_renewal() {
    print_step "设置SSL证书自动续期..."
    
    # 测试续期
    certbot renew --dry-run
    
    if [[ $? -eq 0 ]]; then
        # 添加到crontab
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -
        print_info "✅ SSL证书自动续期设置成功"
    else
        print_warning "⚠️  SSL证书续期测试失败，请手动检查"
    fi
}

# 配置Django项目的HTTPS设置
configure_django_https() {
    print_step "配置Django HTTPS设置..."
    
    if [[ -f "$PROJECT_PATH/.env" ]]; then
        # 更新.env文件中的HTTPS设置
        sed -i "s/DEBUG=True/DEBUG=False/g" "$PROJECT_PATH/.env"
        sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$DOMAIN_NAME,www.$DOMAIN_NAME/g" "$PROJECT_PATH/.env"
        sed -i "s|REDIRECT_URI=.*|REDIRECT_URI=https://$DOMAIN_NAME/|g" "$PROJECT_PATH/.env"
        
        # 确保HTTPS安全设置存在
        if ! grep -q "SECURE_SSL_REDIRECT" "$PROJECT_PATH/.env"; then
            cat >> "$PROJECT_PATH/.env" << EOF

# HTTPS安全配置
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
EOF
        fi
        
        print_info "Django HTTPS配置更新完成"
    else
        print_warning "未找到.env文件，请手动配置Django HTTPS设置"
    fi
}

# 重启服务
restart_services() {
    print_step "重启服务..."
    
    # 重启Nginx
    systemctl restart nginx
    
    # 如果存在Django服务，重启它
    if systemctl is-active --quiet yuantong; then
        systemctl restart yuantong
        print_info "Django服务已重启"
    else
        print_warning "Django服务未运行，请手动启动"
    fi
    
    print_info "服务重启完成"
}

# 验证HTTPS配置
verify_https() {
    print_step "验证HTTPS配置..."
    
    # 等待服务启动
    sleep 5
    
    # 检查HTTP重定向
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN_NAME" || echo "000")
    if [[ "$HTTP_STATUS" == "301" || "$HTTP_STATUS" == "302" ]]; then
        print_info "✅ HTTP重定向正常"
    else
        print_warning "⚠️  HTTP重定向可能有问题 (状态码: $HTTP_STATUS)"
    fi
    
    # 检查HTTPS访问
    HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN_NAME" || echo "000")
    if [[ "$HTTPS_STATUS" == "200" ]]; then
        print_info "✅ HTTPS访问正常"
    else
        print_warning "⚠️  HTTPS访问可能有问题 (状态码: $HTTPS_STATUS)"
    fi
    
    # 检查SSL证书
    SSL_EXPIRY=$(echo | openssl s_client -servername "$DOMAIN_NAME" -connect "$DOMAIN_NAME:443" 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    if [[ -n "$SSL_EXPIRY" ]]; then
        print_info "✅ SSL证书有效，到期时间: $SSL_EXPIRY"
    else
        print_warning "⚠️  无法获取SSL证书信息"
    fi
}

# 显示部署结果
show_deployment_result() {
    print_info ""
    print_info "🎉 HTTPS部署完成！"
    print_info ""
    print_info "📋 部署信息："
    print_info "   域名: $DOMAIN_NAME"
    print_info "   HTTPS地址: https://$DOMAIN_NAME"
    print_info "   SSL证书: Let's Encrypt"
    print_info "   证书路径: /etc/letsencrypt/live/$DOMAIN_NAME/"
    print_info "   Nginx配置: /etc/nginx/sites-available/yuantong"
    print_info ""
    print_info "🔧 管理命令："
    print_info "   查看SSL证书状态: sudo certbot certificates"
    print_info "   手动续期证书: sudo certbot renew"
    print_info "   测试Nginx配置: sudo nginx -t"
    print_info "   重启Nginx: sudo systemctl restart nginx"
    print_info "   查看Nginx日志: sudo tail -f /var/log/nginx/error.log"
    print_info ""
    print_info "🌐 访问地址："
    print_info "   https://$DOMAIN_NAME"
    print_info "   https://www.$DOMAIN_NAME"
    print_info ""
    print_info "🔒 SSL安全评级测试："
    print_info "   https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN_NAME"
    print_info ""
    print_warning "⚠️  重要提醒："
    print_warning "   1. SSL证书有效期90天，已设置自动续期"
    print_warning "   2. 请确保Django应用正常运行"
    print_warning "   3. 建议定期备份SSL证书"
    print_info ""
}

# 主函数
main() {
    print_info "🔐 开始HTTPS部署..."
    
    check_root
    get_user_input
    check_domain_resolution
    install_dependencies
    setup_firewall
    create_temp_nginx_config
    obtain_ssl_certificate
    create_production_nginx_config
    setup_ssl_auto_renewal
    configure_django_https
    restart_services
    verify_https
    show_deployment_result
    
    print_info "✅ HTTPS部署完成！"
}

# 运行主函数
main "$@" 