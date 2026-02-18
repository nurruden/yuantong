#!/bin/bash
# 本地开发环境启动脚本
# 使用方法: ./dev_start.sh [端口号，默认8000]

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 端口号（默认8000）
PORT=${1:-8000}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  远通信息化系统 - 本地开发环境启动${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 检查 Python 版本
echo -e "${YELLOW}[1/6] 检查 Python 版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python 版本: $(python3 --version)"
echo ""

# 2. 检查/创建虚拟环境
echo -e "${YELLOW}[2/6] 检查虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo -e "${GREEN}虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate
echo ""

# 3. 安装/更新依赖
echo -e "${YELLOW}[3/6] 检查并安装依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo -e "${GREEN}依赖安装完成${NC}"
else
    echo -e "${RED}警告: 未找到 requirements.txt${NC}"
fi
echo ""

# 4. 检查环境变量配置
echo -e "${YELLOW}[4/6] 检查环境变量配置...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}未找到 .env 文件，从 .env.example 复制模板...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}请编辑 .env 文件，填入您的配置信息${NC}"
        echo -e "${YELLOW}至少需要配置: SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD${NC}"
        echo ""
        read -p "按 Enter 继续（将使用默认配置，可能无法正常启动）..."
    else
        echo -e "${RED}警告: 未找到 .env 或 .env.example 文件${NC}"
    fi
else
    echo -e "${GREEN}.env 文件已存在${NC}"
fi
echo ""

# 5. 数据库迁移
echo -e "${YELLOW}[5/6] 运行数据库迁移...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}数据库迁移完成${NC}"
echo ""

# 6. 创建超级用户（可选）
echo -e "${YELLOW}[6/6] 检查超级用户...${NC}"
SUPERUSER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).count())" 2>/dev/null || echo "0")
if [ "$SUPERUSER_COUNT" = "0" ]; then
    echo -e "${YELLOW}未找到超级用户，是否创建？(y/n)${NC}"
    read -p "> " CREATE_SUPERUSER
    if [ "$CREATE_SUPERUSER" = "y" ] || [ "$CREATE_SUPERUSER" = "Y" ]; then
        python manage.py createsuperuser
    fi
else
    echo -e "${GREEN}已存在超级用户${NC}"
fi
echo ""

# 7. 收集静态文件（开发环境可选）
echo -e "${YELLOW}[可选] 收集静态文件？(y/n，默认n)${NC}"
read -p "> " COLLECT_STATIC
if [ "$COLLECT_STATIC" = "y" ] || [ "$COLLECT_STATIC" = "Y" ]; then
    python manage.py collectstatic --noinput
    echo -e "${GREEN}静态文件收集完成${NC}"
fi
echo ""

# 8. 启动开发服务器
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  启动 Django 开发服务器...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "访问地址: ${GREEN}http://localhost:${PORT}${NC}"
echo -e "管理后台: ${GREEN}http://localhost:${PORT}/admin/${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo ""

# 启动开发服务器
python manage.py runserver 0.0.0.0:${PORT}
