#!/bin/bash
# 配置企业微信消息接收Token的脚本

echo "=========================================="
echo "企业微信消息接收Token配置工具"
echo "=========================================="
echo ""

# 检查.env文件是否存在
if [ ! -f "/var/www/yuantong/.env" ]; then
    echo "❌ .env文件不存在，正在创建..."
    touch /var/www/yuantong/.env
fi

# 读取现有的Token配置
CURRENT_TOKEN=$(grep "^WECHAT_MESSAGE_TOKEN=" /var/www/yuantong/.env 2>/dev/null | cut -d'=' -f2 | tr -d "'\"")

if [ -n "$CURRENT_TOKEN" ]; then
    echo "当前已配置的Token: $CURRENT_TOKEN"
    echo ""
    read -p "是否要更新Token? (y/n): " update_choice
    if [ "$update_choice" != "y" ] && [ "$update_choice" != "Y" ]; then
        echo "已取消操作"
        exit 0
    fi
fi

echo ""
echo "请输入企业微信管理后台配置的Token:"
echo "（这个Token需要与企业微信管理后台 -> 应用管理 -> 接收消息 -> Token保持一致）"
read -p "Token: " NEW_TOKEN

if [ -z "$NEW_TOKEN" ]; then
    echo "❌ Token不能为空"
    exit 1
fi

# 更新.env文件
if grep -q "^WECHAT_MESSAGE_TOKEN=" /var/www/yuantong/.env; then
    # 如果已存在，则更新
    sed -i "s|^WECHAT_MESSAGE_TOKEN=.*|WECHAT_MESSAGE_TOKEN=$NEW_TOKEN|" /var/www/yuantong/.env
else
    # 如果不存在，则添加
    echo "" >> /var/www/yuantong/.env
    echo "# 企业微信消息接收Token" >> /var/www/yuantong/.env
    echo "WECHAT_MESSAGE_TOKEN=$NEW_TOKEN" >> /var/www/yuantong/.env
fi

echo ""
echo "✅ Token配置已更新"
echo ""
echo "配置的Token: $NEW_TOKEN"
echo ""
echo "⚠️  重要提示："
echo "1. 请确保此Token与企业微信管理后台配置的Token完全一致（区分大小写）"
echo "2. 配置完成后需要重启Django服务"
echo ""
read -p "是否现在重启Django服务? (y/n): " restart_choice

if [ "$restart_choice" == "y" ] || [ "$restart_choice" == "Y" ]; then
    echo "正在重启Django服务..."
    sudo systemctl restart ytbi-django
    sleep 2
    if sudo systemctl is-active --quiet ytbi-django; then
        echo "✅ Django服务已重启"
    else
        echo "❌ Django服务重启失败，请手动检查"
    fi
else
    echo "请稍后手动执行: sudo systemctl restart ytbi-django"
fi

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="

