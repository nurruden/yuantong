#!/bin/bash

# 停止Celery服务的脚本
# 使用方法: ./stop_celery.sh

echo "🛑 停止Celery服务..."

# 停止Celery Worker
echo "👷 停止Celery Worker..."
pkill -f "celery.*worker" || echo "Celery Worker 未运行"

# 停止Celery Beat
echo "⏰ 停止Celery Beat..."
pkill -f "celery.*beat" || echo "Celery Beat 未运行"

# 等待进程完全停止
sleep 2

# 检查是否还有残留进程
if pgrep -f "celery" > /dev/null; then
    echo "⚠️  发现残留的Celery进程，强制终止..."
    pkill -9 -f "celery"
    sleep 1
fi

# 清理PID文件
rm -f /var/www/yuantong/celery_worker.pid
rm -f /var/www/yuantong/celery_beat.pid

echo "✅ Celery服务已停止"
