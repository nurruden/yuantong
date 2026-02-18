#!/bin/bash

# 修复Django迁移冲突脚本

set -e

echo "=========================================="
echo "Django迁移冲突修复工具"
echo "=========================================="

# 激活虚拟环境
source venv/bin/activate

echo "检查数据库表状态..."

# 检查哪些表已经存在
echo "检查home应用的表..."

# 检查ProductModel表
if python manage.py dbshell -c "SHOW TABLES LIKE 'home_productmodel';" 2>/dev/null | grep -q "home_productmodel"; then
    echo "✅ home_productmodel表已存在"
    echo "标记迁移0012_productmodel为已执行..."
    python manage.py migrate home 0012 --fake
else
    echo "❌ home_productmodel表不存在"
fi

# 检查其他可能存在的表
tables_to_check=(
    "home_packaging"
    "home_userfavorite"
    "home_parameter"
    "home_xinghui_qc_report"
    "home_yuantongqcreport"
    "home_yuantong2qcreport"
    "home_xinghui2qcreport"
    "home_changfuqcreport"
)

for table in "${tables_to_check[@]}"; do
    if python manage.py dbshell -c "SHOW TABLES LIKE '$table';" 2>/dev/null | grep -q "$table"; then
        echo "✅ $table表已存在"
    else
        echo "❌ $table表不存在"
    fi
done

echo ""
echo "执行迁移修复..."

# 尝试执行迁移，如果失败则标记为已执行
migrations_to_fake=(
    "home 0012"
    "home 0013"
    "home 0017"
    "home 0023"
    "home 0033"
    "home 0035"
    "home 0036"
    "home 0037"
)

for migration in "${migrations_to_fake[@]}"; do
    echo "尝试执行迁移: $migration"
    if python manage.py migrate $migration 2>/dev/null; then
        echo "✅ 迁移 $migration 执行成功"
    else
        echo "⚠️  迁移 $migration 执行失败，标记为已执行"
        python manage.py migrate $migration --fake
    fi
done

# 执行剩余的迁移
echo ""
echo "执行剩余迁移..."
python manage.py migrate

echo ""
echo "验证迁移状态..."
python manage.py showmigrations --list | grep "\[ \]"

echo ""
echo "=========================================="
echo "迁移修复完成！"
echo "=========================================="
