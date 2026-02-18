# 🚀 远通系统运维命令速查表

## 🎯 快速操作

### 一键脚本
```bash
# 快速修复所有常见问题
sudo ./quick_fix.sh

# 健康检查
./health_check.sh

# 查看系统状态
sudo systemctl status yuantong-django
```

## 🔧 服务管理

### 基础服务操作
```bash
# 启动服务
sudo systemctl start yuantong-django

# 停止服务
sudo systemctl stop yuantong-django

# 重启服务（常用）
sudo systemctl restart yuantong-django

# 重新加载配置（推荐，无需重启）
sudo systemctl reload yuantong-django

# 查看服务状态
sudo systemctl status yuantong-django

# 开机自启
sudo systemctl enable yuantong-django

# 禁用开机自启
sudo systemctl disable yuantong-django
```

### 服务日志查看
```bash
# 查看systemd日志（实时）
sudo journalctl -u yuantong-django -f

# 查看最近50行日志
sudo journalctl -u yuantong-django -n 50

# 查看特定时间段日志
sudo journalctl -u yuantong-django --since "2024-01-01 10:00:00"

# 查看服务启动日志
sudo journalctl -u yuantong-django --since "1 hour ago"
```

## 📋 应用日志

### 日志文件路径
```bash
# 应用错误日志
tail -f /var/www/yuantong/logs/gunicorn_error.log

# 访问日志
tail -f /var/www/yuantong/logs/gunicorn_access.log

# 调试日志
tail -f /var/www/yuantong/logs/debug.log
```

### 日志分析命令
```bash
# 统计今日访问量
grep "$(date '+%d/%b/%Y')" /var/www/yuantong/logs/gunicorn_access.log | wc -l

# 查看最近的错误
grep -i "error" /var/www/yuantong/logs/gunicorn_error.log | tail -10

# 查看企业微信相关日志
grep -i "wechat" /var/www/yuantong/logs/gunicorn_error.log

# 查看最近5分钟的日志
sudo journalctl -u yuantong-django --since="5 minutes ago"

# 查看错误数量
grep -c "ERROR" /var/www/yuantong/logs/gunicorn_error.log
```

## 🗄️ 数据库操作

### Django数据库命令
```bash
cd /var/www/yuantong

# 进入数据库shell
python manage.py dbshell

# 执行数据库迁移
python manage.py migrate

# 创建迁移文件
python manage.py makemigrations

# 查看迁移状态
python manage.py showmigrations

# 清理过期session
python manage.py clearsessions

# 检查应用配置
python manage.py check
```

### 数据库备份与恢复
```bash
# 备份数据库
cp /var/www/yuantong/db.sqlite3 /var/www/yuantong/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 从备份恢复
cp /var/www/yuantong/db.sqlite3.backup.YYYYMMDD_HHMMSS /var/www/yuantong/db.sqlite3

# 检查数据库完整性
echo "PRAGMA integrity_check;" | python manage.py dbshell
```

## 🔍 故障诊断

### 系统状态检查
```bash
# 检查服务是否运行
sudo systemctl is-active yuantong-django

# 检查端口监听
netstat -tlnp | grep :8000
ss -tlnp | grep :8000

# 检查进程
pgrep -f gunicorn
ps aux | grep gunicorn

# 测试连通性
curl -I http://127.0.0.1:8000/
```

### 资源监控
```bash
# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 检查CPU使用
top -p $(pgrep -f gunicorn | tr '\n' ',' | sed 's/,$//')

# 检查网络连接
netstat -an | grep :8000
```

### 权限检查
```bash
# 检查文件所有者
ls -la /var/www/yuantong/

# 检查特定文件权限
stat /var/www/yuantong/.env

# 修复权限
sudo chown -R deploy:deploy /var/www/yuantong
sudo chmod -R 755 /var/www/yuantong
sudo chmod -R 775 /var/www/yuantong/logs
```

## 🔧 企业微信调试

### 环境变量检查
```bash
cd /var/www/yuantong

# 查看企业微信配置
grep WECHAT .env

# 测试企业微信API
curl "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=YOUR_CORP_ID&corpsecret=YOUR_SECRET"
```

### 授权问题排查
```bash
# 查看OAuth相关日志
grep -i "oauth\|wechat" logs/gunicorn_error.log | tail -10

# 检查授权URL配置
grep -A 5 -B 5 "oauth2/authorize" home/views.py

# 清除session缓存
python manage.py clearsessions
```

## 📊 性能优化

### 缓存清理
```bash
cd /var/www/yuantong

# 清理Django缓存
python manage.py clearsessions

# 清理大日志文件
find logs/ -name "*.log" -size +100M -exec rm {} \;

# 压缩旧日志
gzip logs/*.log.old
```

### 静态文件管理
```bash
cd /var/www/yuantong

# 收集静态文件
python manage.py collectstatic --noinput

# 检查静态文件权限
ls -la static/
```

## 🔄 更新部署

### 应用更新流程
```bash
# 1. 备份当前版本
cd /var/www
sudo tar -czf yuantong_backup_$(date +%Y%m%d_%H%M%S).tar.gz yuantong/

# 2. 拉取最新代码
cd /var/www/yuantong
sudo -u deploy git pull origin main

# 3. 安装依赖
sudo -u deploy pip install -r requirements.txt

# 4. 数据库迁移
sudo -u deploy python manage.py migrate

# 5. 收集静态文件
sudo -u deploy python manage.py collectstatic --noinput

# 6. 重启服务
sudo systemctl restart yuantong-django

# 7. 验证部署
sudo systemctl status yuantong-django
curl -I http://localhost:8000/
```

## 🚨 紧急响应

### 紧急恢复命令
```bash
# 立即重启所有相关服务
sudo systemctl restart yuantong-django nginx

# 如果服务无法启动，查看详细错误
sudo journalctl -u yuantong-django --no-pager | tail -20

# 从备份快速恢复数据库
cd /var/www/yuantong
cp db.sqlite3 db.sqlite3.broken
cp /var/backups/yuantong/db_*.sqlite3 db.sqlite3
sudo systemctl restart yuantong-django
```

### 问题分级处理

#### 🟢 P3 - 轻微问题
- 响应时间稍慢 → `sudo systemctl reload yuantong-django`
- 日志文件过大 → 清理日志文件
- 内存使用较高 → `sudo systemctl restart yuantong-django`

#### 🟡 P2 - 中等问题
- 企业微信授权失败 → 检查环境变量 + 重启服务
- 数据库连接问题 → 检查数据库文件权限
- 部分功能异常 → 查看应用日志

#### 🔴 P1 - 严重问题
- 服务完全无法访问 → 执行 `sudo ./quick_fix.sh`
- 数据库损坏 → 从备份恢复
- 系统资源耗尽 → 立即重启服务器

## 📞 联系信息

### 技术支持
- **紧急联系**: [电话号码]
- **邮件支持**: [邮箱地址]
- **工作时间**: 9:00-18:00

### 外部依赖
- **企业微信**: qyapi.weixin.qq.com
- **EAS系统**: [EAS服务器地址]

---
*快捷键: Ctrl+F 搜索命令* 