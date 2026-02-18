#!/bin/bash

# 远通系统健康检查脚本
# 使用方法: ./health_check.sh

echo "🏥 远通信息化系统健康检查"
echo "========================="
echo "检查时间: $(date)"
echo

# 定义项目路径
PROJECT_DIR="/var/www/yuantong"
LOG_DIR="$PROJECT_DIR/logs"

# 检查项目数组
checks=()
warnings=()
errors=()

echo "🔍 开始系统检查..."
echo

# 1. 服务状态检查
echo "1️⃣ 检查Django服务状态..."
if systemctl is-active --quiet yuantong-django; then
    service_status=$(systemctl show yuantong-django --property=ActiveState,SubState --no-pager)
    checks+=("✅ Django服务运行正常 ($service_status)")
    
    # 检查服务运行时间
    uptime=$(systemctl show yuantong-django --property=ActiveEnterTimestamp --no-pager | cut -d'=' -f2)
    if [ ! -z "$uptime" ]; then
        checks+=("📅 服务启动时间: $uptime")
    fi
else
    errors+=("❌ Django服务未运行")
    # 获取失败原因
    failed_reason=$(systemctl show yuantong-django --property=Result --no-pager | cut -d'=' -f2)
    errors+=("   失败原因: $failed_reason")
fi

# 2. 端口监听检查
echo "2️⃣ 检查端口监听状态..."
port_count=$(netstat -tlnp 2>/dev/null | grep ":8000" | wc -l)
if [ "$port_count" -gt 0 ]; then
    port_info=$(netstat -tlnp 2>/dev/null | grep ":8000")
    checks+=("✅ 端口8000正常监听 ($port_count 个)")
    checks+=("   $port_info")
else
    errors+=("❌ 端口8000未监听")
fi

# 3. 进程检查
echo "3️⃣ 检查应用进程..."
gunicorn_count=$(pgrep -f gunicorn | wc -l)
if [ "$gunicorn_count" -gt 0 ]; then
    checks+=("✅ Gunicorn进程运行正常 ($gunicorn_count 个进程)")
    
    # 检查进程内存使用
    mem_usage=$(ps aux | grep gunicorn | grep -v grep | awk '{sum+=$6} END {if(sum) print sum/1024; else print 0}')
    if (( $(echo "$mem_usage > 0" | bc -l) )); then
        checks+=("💾 内存使用: ${mem_usage} MB")
    fi
else
    errors+=("❌ 没有Gunicorn进程运行")
fi

# 4. 文件权限检查
echo "4️⃣ 检查文件权限..."
if [ -d "$PROJECT_DIR" ]; then
    owner=$(stat -c "%U:%G" "$PROJECT_DIR")
    if [ "$owner" = "deploy:deploy" ]; then
        checks+=("✅ 文件权限正确 ($owner)")
    else
        errors+=("❌ 文件权限错误: $owner (应该是 deploy:deploy)")
    fi
    
    # 检查关键文件权限
    if [ -f "$PROJECT_DIR/.env" ]; then
        env_perm=$(stat -c "%a" "$PROJECT_DIR/.env")
        if [ "$env_perm" = "644" ] || [ "$env_perm" = "600" ]; then
            checks+=("✅ .env文件权限正确 ($env_perm)")
        else
            warnings+=("⚠️ .env文件权限可能不安全: $env_perm")
        fi
    else
        errors+=("❌ .env文件不存在")
    fi
else
    errors+=("❌ 项目目录不存在: $PROJECT_DIR")
fi

# 5. 磁盘空间检查
echo "5️⃣ 检查磁盘空间..."
if [ -d "$PROJECT_DIR" ]; then
    disk_usage=$(df "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    disk_available=$(df -h "$PROJECT_DIR" | awk 'NR==2 {print $4}')
    
    if [ "$disk_usage" -lt 80 ]; then
        checks+=("✅ 磁盘空间充足 (已用${disk_usage}%, 可用${disk_available})")
    elif [ "$disk_usage" -lt 90 ]; then
        warnings+=("⚠️ 磁盘空间紧张: 已用${disk_usage}%, 可用${disk_available}")
    else
        errors+=("❌ 磁盘空间不足: 已用${disk_usage}%, 可用${disk_available}")
    fi
fi

# 6. 内存使用检查
echo "6️⃣ 检查系统内存..."
mem_info=$(free | awk 'NR==2{printf "使用: %.0f%% (%.1fG/%.1fG)", $3*100/$2, $3/1024/1024, $2/1024/1024}')
mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')

if [ "$mem_usage" -lt 80 ]; then
    checks+=("✅ 内存使用正常 ($mem_info)")
elif [ "$mem_usage" -lt 90 ]; then
    warnings+=("⚠️ 内存使用较高: $mem_info")
else
    errors+=("❌ 内存使用过高: $mem_info")
fi

# 7. 数据库检查
echo "7️⃣ 检查数据库..."
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    db_size=$(ls -lh "$PROJECT_DIR/db.sqlite3" | awk '{print $5}')
    checks+=("✅ 数据库文件存在 (大小: $db_size)")
    
    # 尝试检查数据库完整性（如果可以的话）
    cd "$PROJECT_DIR" 2>/dev/null && {
        if command -v python >/dev/null 2>&1; then
            db_check=$(echo "PRAGMA integrity_check;" | python manage.py dbshell 2>/dev/null | head -1)
            if [ "$db_check" = "ok" ]; then
                checks+=("✅ 数据库完整性检查通过")
            else
                warnings+=("⚠️ 数据库完整性检查异常: $db_check")
            fi
        fi
    }
else
    errors+=("❌ 数据库文件不存在")
fi

# 8. 响应时间检查
echo "8️⃣ 检查服务响应时间..."
if systemctl is-active --quiet yuantong-django && netstat -tlnp | grep -q ":8000"; then
    response_time=$(curl -o /dev/null -s -w "%{time_total}" http://127.0.0.1:8000/ 2>/dev/null || echo "999")
    
    if (( $(echo "$response_time < 2.0" | bc -l 2>/dev/null || echo 0) )); then
        checks+=("✅ 响应时间正常 (${response_time}秒)")
    elif (( $(echo "$response_time < 5.0" | bc -l 2>/dev/null || echo 0) )); then
        warnings+=("⚠️ 响应时间较慢: ${response_time}秒")
    else
        if [ "$response_time" = "999" ]; then
            errors+=("❌ 无法连接到服务")
        else
            errors+=("❌ 响应时间过慢: ${response_time}秒")
        fi
    fi
fi

# 9. 日志检查
echo "9️⃣ 检查日志状态..."
if [ -d "$LOG_DIR" ]; then
    log_size=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')
    checks+=("✅ 日志目录存在 (大小: $log_size)")
    
    # 检查最近的错误
    if [ -f "$LOG_DIR/gunicorn_error.log" ]; then
        recent_errors=$(grep -c "ERROR" "$LOG_DIR/gunicorn_error.log" 2>/dev/null || echo 0)
        if [ "$recent_errors" -lt 5 ]; then
            checks+=("✅ 错误日志正常 ($recent_errors 个错误)")
        elif [ "$recent_errors" -lt 20 ]; then
            warnings+=("⚠️ 发现一些错误: $recent_errors 个ERROR")
        else
            errors+=("❌ 发现大量错误: $recent_errors 个ERROR")
        fi
    fi
else
    warnings+=("⚠️ 日志目录不存在")
fi

# 10. 环境变量检查
echo "🔟 检查环境配置..."
if [ -f "$PROJECT_DIR/.env" ]; then
    wechat_config=$(grep -c "WECHAT_" "$PROJECT_DIR/.env" 2>/dev/null || echo 0)
    if [ "$wechat_config" -ge 3 ]; then
        checks+=("✅ 企业微信配置完整")
    else
        warnings+=("⚠️ 企业微信配置可能不完整")
    fi
fi

echo
echo "📊 检查完成！"
echo "=============="

# 输出结果
if [ ${#checks[@]} -gt 0 ]; then
    echo
    echo "✅ 正常项目 (${#checks[@]} 项):"
    for check in "${checks[@]}"; do
        echo "  $check"
    done
fi

if [ ${#warnings[@]} -gt 0 ]; then
    echo
    echo "⚠️ 警告项目 (${#warnings[@]} 项):"
    for warning in "${warnings[@]}"; do
        echo "  $warning"
    done
fi

if [ ${#errors[@]} -gt 0 ]; then
    echo
    echo "❌ 错误项目 (${#errors[@]} 项):"
    for error in "${errors[@]}"; do
        echo "  $error"
    done
    echo
    echo "🔧 建议执行快速修复:"
    echo "   sudo ./quick_fix.sh"
    echo
    echo "📝 查看详细日志:"
    echo "   sudo journalctl -u yuantong-django -f"
    echo "   tail -f $PROJECT_DIR/logs/gunicorn_error.log"
    
    exit 1
else
    if [ ${#warnings[@]} -gt 0 ]; then
        echo
        echo "🎗️ 系统运行基本正常，但有一些需要注意的地方"
        exit 2
    else
        echo
        echo "🎉 系统运行状态完全正常！"
        exit 0
    fi
fi 