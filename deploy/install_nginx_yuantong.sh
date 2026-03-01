#!/bin/bash
# 在 10.0.2.2 服务器上执行，部署 jilinyuantong.top 的 Nginx 配置
# 用法：sudo bash deploy/install_nginx_yuantong.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_SRC="$PROJECT_DIR/deploy/nginx_yuantong.conf"

if [ ! -f "$CONFIG_SRC" ]; then
    echo "错误: 找不到 $CONFIG_SRC"
    exit 1
fi

# Debian/Ubuntu 使用 sites-available
if [ -d /etc/nginx/sites-available ]; then
    sudo cp "$CONFIG_SRC" /etc/nginx/sites-available/yuantong
    sudo ln -sf /etc/nginx/sites-available/yuantong /etc/nginx/sites-enabled/
    echo "已复制到 /etc/nginx/sites-available/yuantong"
# CentOS/RHEL 使用 conf.d
elif [ -d /etc/nginx/conf.d ]; then
    sudo cp "$CONFIG_SRC" /etc/nginx/conf.d/yuantong.conf
    echo "已复制到 /etc/nginx/conf.d/yuantong.conf"
else
    echo "错误: 无法确定 Nginx 配置目录"
    exit 1
fi

echo "检查 Nginx 配置..."
sudo nginx -t

echo "重载 Nginx..."
sudo systemctl reload nginx

echo "部署完成。"
