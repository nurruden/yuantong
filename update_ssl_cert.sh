#!/bin/bash

# 🔐 SSL 证书更新脚本
# 用于手动更新 Let's Encrypt SSL 证书
# 使用方法: sudo ./update_ssl_cert.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 开始更新 SSL 证书...${NC}"

# 检查 root 权限
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}❌ 此脚本需要 root 权限运行${NC}"
    echo "请使用: sudo $0"
    exit 1
fi

# 查找 certbot 路径
CERTBOT=""
for path in /usr/bin/certbot /usr/local/bin/certbot /home/deploy/.local/bin/certbot; do
    if [[ -x "$path" ]]; then
        CERTBOT="$path"
        break
    fi
done

if [[ -z "$CERTBOT" ]]; then
    echo -e "${RED}❌ 未找到 certbot，请先安装:${NC}"
    echo "  CentOS/RHEL: yum install -y certbot python3-certbot-nginx"
    echo "  Ubuntu/Debian: apt install -y certbot python3-certbot-nginx"
    exit 1
fi

echo -e "${GREEN}✓ 使用 certbot: $CERTBOT${NC}"

# 1. 检查当前证书状态
echo ""
echo -e "${BLUE}[1/4] 检查当前证书状态...${NC}"
$CERTBOT certificates 2>/dev/null || true

# 2. 模拟续期测试
echo ""
echo -e "${BLUE}[2/4] 执行续期模拟测试 (dry-run)...${NC}"
if $CERTBOT renew --dry-run; then
    echo -e "${GREEN}✓ 模拟测试通过${NC}"
else
    echo -e "${YELLOW}⚠ 模拟测试失败，但仍将尝试实际续期${NC}"
    read -p "是否继续执行实际续期? (y/n): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. 执行实际续期
echo ""
echo -e "${BLUE}[3/4] 执行证书续期...${NC}"
if $CERTBOT renew --quiet; then
    echo -e "${GREEN}✓ 证书续期成功${NC}"
else
    # 如果证书未到续期时间，certbot renew 可能不执行任何操作
    # 使用 --force-renewal 强制续期
    echo -e "${YELLOW}⚠ 常规续期未执行（可能未到续期时间）${NC}"
    read -p "是否强制续期证书? (y/n): " force_confirm
    if [[ $force_confirm =~ ^[Yy]$ ]]; then
        $CERTBOT renew --force-renewal
        echo -e "${GREEN}✓ 强制续期完成${NC}"
    fi
fi

# 4. 重载 Nginx
echo ""
echo -e "${BLUE}[4/4] 重载 Nginx 配置...${NC}"
if nginx -t 2>/dev/null; then
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx 已重载${NC}"
else
    echo -e "${YELLOW}⚠ Nginx 配置测试失败，请手动检查${NC}"
fi

# 验证结果
echo ""
echo -e "${BLUE}📋 验证新证书...${NC}"
if [[ -f /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem ]]; then
    echo "证书有效期:"
    openssl x509 -in /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem -noout -dates
fi

echo ""
echo -e "${GREEN}✅ SSL 证书更新完成！${NC}"
echo ""
echo "📌 提示："
echo "  - 查看证书状态: sudo certbot certificates"
echo "  - 自动续期已配置在 crontab (每天 12:00)"
echo "  - 测试 HTTPS: curl -I https://jilinyuantong.top/"
