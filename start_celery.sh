#!/bin/bash

# 启动Celery服务的脚本
# 使用方法: ./start_celery.sh

set -e

echo "🚀 启动Celery服务..."

# 检查虚拟环境
if [ ! -d "/var/www/yuantong/venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source /var/www/yuantong/venv/bin/activate

# 检查Redis是否运行
if ! pgrep redis-server > /dev/null; then
    echo "⚠️  Redis未运行，正在启动Redis..."
    sudo systemctl start redis-server
    sleep 2
fi

# 创建日志目录
mkdir -p /var/www/yuantong/logs

# 停止现有的Celery进程
echo "🛑 停止现有Celery进程..."
pkill -f "celery.*worker" || true
pkill -f "celery.*beat" || true

# 等待进程完全停止
sleep 2

# 启动Celery Worker
echo "👷 启动Celery Worker..."
cd /var/www/yuantong
nohup /var/www/yuantong/venv/bin/celery -A yuantong worker --loglevel=info --logfile=/var/www/yuantong/logs/celery_worker.log --pidfile=/var/www/yuantong/celery_worker.pid --detach

# 启动Celery Beat
echo "⏰ 启动Celery Beat..."
nohup /var/www/yuantong/venv/bin/celery -A yuantong beat --loglevel=info --logfile=/var/www/yuantong/logs/celery_beat.log --pidfile=/var/www/yuantong/celery_beat.pid --detach --scheduler django_celery_beat.schedulers:DatabaseScheduler

# 等待服务启动
sleep 3

# 检查服务状态
echo "📊 检查服务状态..."
if pgrep -f "celery.*worker" > /dev/null; then
    echo "✅ Celery Worker 运行正常"
else
    echo "❌ Celery Worker 启动失败"
fi

if pgrep -f "celery.*beat" > /dev/null; then
    echo "✅ Celery Beat 运行正常"
else
    echo "❌ Celery Beat 启动失败"
fi

echo "🎉 Celery服务启动完成！"
echo "📝 日志文件位置："
echo "   - Worker: /var/www/yuantong/logs/celery_worker.log"
echo "   - Beat: /var/www/yuantong/logs/celery_beat.log"
