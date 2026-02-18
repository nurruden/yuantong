#!/bin/bash

# 远通项目日志管理脚本
# 作者: AI Assistant
# 日期: $(date +%Y-%m-%d)

PROJECT_DIR="/var/www/yuantong"
LOG_DIR="$PROJECT_DIR/logs"
LOGROTATE_CONFIG="/etc/logrotate.d/yuantong"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "远通项目日志管理脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  status      显示日志文件状态"
    echo "  rotate      手动执行日志轮转"
    echo "  test        测试logrotate配置"
    echo "  clean       清理超过指定天数的日志文件"
    echo "  monitor     监控日志文件大小"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status"
    echo "  $0 rotate"
    echo "  $0 clean 90"
}

# 显示日志文件状态
show_status() {
    print_info "检查日志文件状态..."
    echo ""
    
    if [ -d "$LOG_DIR" ]; then
        print_info "应用日志文件 ($LOG_DIR):"
        ls -lh "$LOG_DIR"/*.log 2>/dev/null || print_warning "没有找到应用日志文件"
        echo ""
        
        print_info "应用日志轮转文件:"
        ls -lh "$LOG_DIR"/*.log.* 2>/dev/null || print_info "没有轮转文件"
        echo ""
    else
        print_error "日志目录不存在: $LOG_DIR"
    fi
    
    print_info "Nginx日志文件:"
    ls -lh /var/log/nginx/yuantong*.log 2>/dev/null || print_warning "没有找到Nginx日志文件"
    echo ""
    
    print_info "Nginx日志轮转文件:"
    ls -lh /var/log/nginx/yuantong*.log.* 2>/dev/null || print_info "没有轮转文件"
    echo ""
    
    print_info "磁盘使用情况:"
    df -h "$LOG_DIR" 2>/dev/null || df -h /var/log
}

# 手动执行日志轮转
manual_rotate() {
    print_info "执行手动日志轮转..."
    
    if [ ! -f "$LOGROTATE_CONFIG" ]; then
        print_error "logrotate配置文件不存在: $LOGROTATE_CONFIG"
        return 1
    fi
    
    # 强制执行轮转
    sudo logrotate -f "$LOGROTATE_CONFIG"
    
    if [ $? -eq 0 ]; then
        print_success "日志轮转执行成功"
    else
        print_error "日志轮转执行失败"
        return 1
    fi
}

# 测试logrotate配置
test_config() {
    print_info "测试logrotate配置..."
    
    if [ ! -f "$LOGROTATE_CONFIG" ]; then
        print_error "logrotate配置文件不存在: $LOGROTATE_CONFIG"
        return 1
    fi
    
    sudo logrotate -d "$LOGROTATE_CONFIG"
    
    if [ $? -eq 0 ]; then
        print_success "配置测试通过"
    else
        print_error "配置测试失败"
        return 1
    fi
}

# 清理旧日志文件
clean_logs() {
    local days=${1:-90}
    print_info "清理超过 $days 天的日志文件..."
    
    # 清理应用日志
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "*.log.*" -type f -mtime +$days -exec ls -lh {} \; 2>/dev/null
        read -p "确认删除以上文件吗? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            find "$LOG_DIR" -name "*.log.*" -type f -mtime +$days -delete
            print_success "应用日志清理完成"
        else
            print_info "取消清理操作"
        fi
    fi
    
    # 清理Nginx日志
    find /var/log/nginx -name "yuantong*.log.*" -type f -mtime +$days -exec ls -lh {} \; 2>/dev/null
    read -p "确认删除以上Nginx日志文件吗? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        sudo find /var/log/nginx -name "yuantong*.log.*" -type f -mtime +$days -delete
        print_success "Nginx日志清理完成"
    else
        print_info "取消Nginx日志清理操作"
    fi
}

# 监控日志文件大小
monitor_logs() {
    print_info "监控日志文件大小..."
    echo ""
    
    # 设置大小阈值 (MB)
    local threshold=100
    
    if [ -d "$LOG_DIR" ]; then
        for logfile in "$LOG_DIR"/*.log; do
            if [ -f "$logfile" ]; then
                size=$(du -m "$logfile" | cut -f1)
                if [ $size -gt $threshold ]; then
                    print_warning "$(basename $logfile): ${size}MB (超过阈值 ${threshold}MB)"
                else
                    print_info "$(basename $logfile): ${size}MB"
                fi
            fi
        done
    fi
    
    # 检查Nginx日志
    for logfile in /var/log/nginx/yuantong*.log; do
        if [ -f "$logfile" ]; then
            size=$(du -m "$logfile" | cut -f1)
            if [ $size -gt $threshold ]; then
                print_warning "$(basename $logfile): ${size}MB (超过阈值 ${threshold}MB)"
            else
                print_info "$(basename $logfile): ${size}MB"
            fi
        fi
    done
}

# 主程序
case "$1" in
    status)
        show_status
        ;;
    rotate)
        manual_rotate
        ;;
    test)
        test_config
        ;;
    clean)
        clean_logs "$2"
        ;;
    monitor)
        monitor_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知选项: $1"
        echo "使用 '$0 help' 查看帮助信息"
        exit 1
        ;;
esac 