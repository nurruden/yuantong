#!/bin/bash
# 系统健康检查脚本

cd /var/www/yuantong

# 激活虚拟环境
source venv/bin/activate

# 运行Python检查脚本
python3 check_system_health.py

