#!/bin/bash

# 生产环境安全配置脚本
# 使用方法: sudo ./production_security_setup.sh

set -e

echo "🛡️ 开始生产环境安全配置..."

# 1. 创建安全的环境变量文件
echo "📝 创建生产环境配置文件..."
cat > /var/www/yuantong/.env.production << 'EOF'
# Django 生产环境配置
SECRET_KEY=your_production_secret_key_minimum_50_characters_long_random_string
DEBUG=False
ALLOWED_HOSTS=jilinyuantong.top,www.jilinyuantong.top,123.249.75.132

# 数据库配置
DB_NAME=yuantongOfficial
DB_USER=yuantong_prod
DB_PASSWORD=your_very_strong_db_password_123!@#$%^&*
DB_HOST=localhost
DB_PORT=3306

# 企业微信配置
WECHAT_CORP_ID=ww3579e18459d4e719
WECHAT_APP_SECRET=tj-a2zCrfSrCSFwRN-KJ9E3eRoa4BMybooBzxOXkPE4
WECHAT_AGENT_ID=1000016
REDIRECT_URI=https://jilinyuantong.top/wechat/callback/

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
X_FRAME_OPTIONS=SAMEORIGIN

# Redis配置
REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/1

# 邮件配置
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@jilinyuantong.top
SERVER_EMAIL=server@jilinyuantong.top
ADMINS=admin@jilinyuantong.top
EOF

# 2. 设置文件权限
echo "🔒 设置环境变量文件权限..."
chown root:www-data /var/www/yuantong/.env.production
chmod 640 /var/www/yuantong/.env.production

# 3. 安装Redis (用于缓存和会话存储)
echo "📦 安装Redis..."
apt update
apt install -y redis-server
systemctl enable redis-server
systemctl start redis-server

# 4. 配置Redis安全
echo "🔐 配置Redis安全..."
sed -i 's/# requirepass foobared/requirepass your_redis_password_here/' /etc/redis/redis.conf
sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
systemctl restart redis-server

# 5. 安装fail2ban (防止暴力破解)
echo "🛡️ 安装fail2ban..."
apt install -y fail2ban

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true
EOF

systemctl enable fail2ban
systemctl start fail2ban

# 6. 配置防火墙
echo "🔥 配置防火墙..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 7. 创建数据库备份脚本
echo "💾 创建数据库备份脚本..."
mkdir -p /var/backups/yuantong

cat > /usr/local/bin/backup_yuantong.sh << 'EOF'
#!/bin/bash
# 数据库备份脚本

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/yuantong"
DB_NAME="yuantongOfficial"
DB_USER="yuantong_prod"
DB_PASSWORD="your_very_strong_db_password_123!@#$%^&*"

# 创建数据库备份
mysqldump -u$DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 创建应用文件备份
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz -C /var/www yuantong --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='logs/*.log'

# 删除7天前的备份
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
EOF

chmod +x /usr/local/bin/backup_yuantong.sh

# 8. 设置自动备份定时任务
echo "⏰ 设置自动备份定时任务..."
crontab -l 2>/dev/null | { cat; echo "0 2 * * * /usr/local/bin/backup_yuantong.sh >> /var/log/backup.log 2>&1"; } | crontab -

# 9. 创建日志轮转配置
echo "📋 配置日志轮转..."
cat > /etc/logrotate.d/yuantong << 'EOF'
/var/www/yuantong/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload gunicorn-yuantong
    endscript
}
EOF

# 10. 创建系统监控脚本
echo "📊 创建系统监控脚本..."
cat > /usr/local/bin/monitor_yuantong.sh << 'EOF'
#!/bin/bash
# 系统监控脚本

LOGFILE="/var/log/yuantong_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查Django进程
if ! pgrep -f "gunicorn.*yuantong" > /dev/null; then
    echo "[$DATE] WARNING: Django/Gunicorn进程未运行" >> $LOGFILE
    systemctl restart gunicorn-yuantong
fi

# 检查Nginx进程
if ! pgrep nginx > /dev/null; then
    echo "[$DATE] WARNING: Nginx进程未运行" >> $LOGFILE
    systemctl restart nginx
fi

# 检查Redis进程
if ! pgrep redis-server > /dev/null; then
    echo "[$DATE] WARNING: Redis进程未运行" >> $LOGFILE
    systemctl restart redis-server
fi

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: 磁盘使用率超过80%: $DISK_USAGE%" >> $LOGFILE
fi

# 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "[$DATE] WARNING: 内存使用率超过80%: $MEM_USAGE%" >> $LOGFILE
fi
EOF

chmod +x /usr/local/bin/monitor_yuantong.sh

# 11. 设置监控定时任务
crontab -l 2>/dev/null | { cat; echo "*/5 * * * * /usr/local/bin/monitor_yuantong.sh"; } | crontab -

# 12. 设置SSL证书自动续期
echo "🔐 设置SSL证书自动续期..."
crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx"; } | crontab -

echo "✅ 生产环境安全配置完成！"
echo ""
echo "⚠️  请务必修改以下配置："
echo "1. /var/www/yuantong/.env.production 中的密码和密钥"
echo "2. /etc/redis/redis.conf 中的Redis密码"
echo "3. /usr/local/bin/backup_yuantong.sh 中的数据库密码"
echo "4. 配置邮件服务器用于错误通知"
echo ""
echo "📋 建议的后续操作："
echo "1. 定期检查 /var/log/yuantong_monitor.log"
echo "2. 定期检查 /var/log/backup.log"
echo "3. 定期更新系统: apt update && apt upgrade"
echo "4. 监控SSL证书到期时间: certbot certificates" 