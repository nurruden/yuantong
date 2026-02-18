#!/bin/bash

# Django 更新部署脚本
# 适用于 model、view、URL 等代码更新

set -e

echo "🚀 开始 Django 应用更新部署..."

# 配置变量
PROJECT_DIR="/var/www/yuantong"
BACKUP_DIR="/var/www/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="yuantong_backup_${TIMESTAMP}"

# 颜色输出函数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

# 1. 创建备份
echo "📦 步骤 1: 创建系统备份..."
mkdir -p "$BACKUP_DIR"
cd /var/www
tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" yuantong/
print_success "备份已创建: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"

# 2. 进入项目目录
cd "$PROJECT_DIR"
print_info "当前工作目录: $(pwd)"

# 3. 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 4. 安装/更新依赖
echo "📦 步骤 2: 更新 Python 依赖..."
pip install -r requirements.txt
print_success "依赖更新完成"

# 5. 检查 Django 配置
echo "🔍 步骤 3: 检查 Django 配置..."
python manage.py check --deploy
print_success "Django 配置检查通过"

# 6. 收集静态文件
echo "📁 步骤 4: 收集静态文件..."
python manage.py collectstatic --noinput --clear
print_success "静态文件收集完成"

# 7. 数据库迁移
echo "🗄️  步骤 5: 执行数据库迁移..."

# 检查是否有待迁移的文件
MIGRATION_STATUS=$(python manage.py showmigrations --list | grep -c "\[ \]" || true)

if [ "$MIGRATION_STATUS" -gt 0 ]; then
    print_info "发现 $MIGRATION_STATUS 个待迁移的变更"
    
    # 显示迁移计划
    echo "迁移计划:"
    python manage.py showmigrations --list | grep "\[ \]"
    
    # 执行迁移
    python manage.py migrate
    print_success "数据库迁移完成"
else
    print_info "没有新的数据库迁移"
fi

# 8. 重启服务
echo "🔄 步骤 6: 重启 Django 服务..."
systemctl restart yuantong-django
print_success "Django 服务已重启"

# 9. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 10. 验证服务状态
echo "🔍 步骤 7: 验证服务状态..."
if systemctl is-active --quiet yuantong-django; then
    print_success "Django 服务运行正常"
else
    print_error "Django 服务启动失败"
    echo "查看服务状态:"
    systemctl status yuantong-django --no-pager
    exit 1
fi

# 11. 健康检查
echo "🏥 步骤 8: 执行健康检查..."
if [ -f "health_check.sh" ]; then
    ./health_check.sh
else
    print_warning "健康检查脚本不存在，跳过"
fi

# 12. 清理缓存（如果有Redis）
echo "🧹 步骤 9: 清理缓存..."
if command -v redis-cli &> /dev/null; then
    redis-cli flushall
    print_success "Redis 缓存已清理"
else
    print_info "Redis 未安装，跳过缓存清理"
fi

# 13. 显示更新结果
echo ""
print_success "🎉 Django 应用更新完成！"
echo ""
echo "📊 更新摘要:"
echo "  • 备份位置: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "  • 服务状态: $(systemctl is-active yuantong-django)"
echo "  • 进程数量: $(pgrep -f gunicorn | wc -l)"
echo "  • 更新时间: $(date)"
echo ""

# 14. 显示有用的命令
echo "🔧 有用的命令:"
echo "  • 查看服务状态: systemctl status yuantong-django"
echo "  • 查看实时日志: journalctl -u yuantong-django -f"
echo "  • 查看错误日志: tail -f logs/gunicorn_error.log"
echo "  • 回滚备份: tar -xzf $BACKUP_DIR/${BACKUP_NAME}.tar.gz -C /var/www/"
echo ""

print_info "更新部署完成！如有问题请检查日志文件。" 