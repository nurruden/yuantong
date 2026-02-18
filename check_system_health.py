#!/usr/bin/env python3
"""
系统健康检查脚本
检查Django、Celery、数据库等关键服务的运行状态
"""
import os
import sys
import subprocess
import requests
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/var/www/yuantong')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuantong.settings')

import django
django.setup()

from django.db import connection
from django.conf import settings
from django_celery_beat.models import PeriodicTask


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def check_service_status(service_name):
    """检查systemd服务状态"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() == 'active'
    except Exception as e:
        return False


def check_port_listening(port):
    """检查端口是否在监听"""
    try:
        result = subprocess.run(
            ['netstat', '-tlnp'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return f':{port}' in result.stdout or f'0.0.0.0:{port}' in result.stdout
    except:
        try:
            result = subprocess.run(
                ['ss', '-tlnp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return f':{port}' in result.stdout or f'0.0.0.0:{port}' in result.stdout
        except:
            return None


def check_process_running(pattern):
    """检查进程是否运行"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )
        # 更精确的匹配：确保是celery进程而不是grep进程
        processes = []
        for line in result.stdout.split('\n'):
            if pattern.lower() in line.lower() and 'python' in line.lower() and 'grep' not in line.lower():
                processes.append(line)
        return len(processes) > 0, processes
    except:
        return False, []


def check_django_service():
    """检查Django服务"""
    print_header("1. Django服务检查")
    
    service_name = 'yuantong-django'
    is_active = check_service_status(service_name)
    
    if is_active:
        print_success(f"Django服务 ({service_name}) 正在运行")
    else:
        print_error(f"Django服务 ({service_name}) 未运行")
        print_info(f"启动命令: sudo systemctl start {service_name}")
    
    # 检查端口8000
    port_listening = check_port_listening(8000)
    if port_listening:
        print_success("端口 8000 正在监听")
    else:
        print_warning("端口 8000 未监听（可能通过socket通信）")
    
    # 检查进程
    gunicorn_running, processes = check_process_running('gunicorn')
    if gunicorn_running:
        print_success(f"Gunicorn进程正在运行 ({len(processes)} 个进程)")
    else:
        print_error("Gunicorn进程未运行")
    
    # 检查HTTP响应
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=3)
        if response.status_code in [200, 301, 302]:
            print_success("Django应用可以正常响应HTTP请求")
        else:
            print_warning(f"Django应用响应异常，状态码: {response.status_code}")
    except Exception as e:
        print_warning(f"无法连接到Django应用: {str(e)}")
    
    return is_active


def check_celery_services():
    """检查Celery服务"""
    print_header("2. Celery服务检查")
    
    # 检查Celery Beat
    beat_running, beat_processes = check_process_running('beat')
    if beat_running:
        print_success(f"Celery Beat正在运行 ({len(beat_processes)} 个进程)")
    else:
        print_error("Celery Beat未运行")
        print_info("启动命令: celery -A yuantong beat -l info")
    
    # 检查Celery Worker
    worker_running, worker_processes = check_process_running('worker')
    if worker_running:
        # 过滤掉beat进程，只统计worker进程
        worker_only = [p for p in worker_processes if 'worker' in p.lower() and 'beat' not in p.lower()]
        worker_count = len(worker_only)
        print_success(f"Celery Worker正在运行 ({worker_count} 个worker进程)")
    else:
        print_error("Celery Worker未运行")
        print_info("启动命令: celery -A yuantong worker -l info")
    
    # 检查定时任务
    try:
        enabled_tasks = PeriodicTask.objects.filter(enabled=True).count()
        total_tasks = PeriodicTask.objects.count()
        print_info(f"定时任务: {enabled_tasks}/{total_tasks} 个已启用")
        
        if enabled_tasks > 0:
            print_success(f"有 {enabled_tasks} 个启用的定时任务")
        else:
            print_warning("没有启用的定时任务")
    except Exception as e:
        print_error(f"检查定时任务失败: {str(e)}")
    
    return beat_running and worker_running


def check_database():
    """检查数据库连接"""
    print_header("3. 数据库检查")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print_success("数据库连接正常")
                
                # 检查数据库名称
                db_name = settings.DATABASES['default']['NAME']
                print_info(f"数据库名称: {db_name}")
                
                # 检查数据库引擎
                db_engine = settings.DATABASES['default']['ENGINE']
                print_info(f"数据库引擎: {db_engine.split('.')[-1]}")
                
                return True
    except Exception as e:
        print_error(f"数据库连接失败: {str(e)}")
        return False


def check_environment_variables():
    """检查关键环境变量"""
    print_header("4. 环境变量检查")
    
    required_vars = {
        'WECHAT_CORP_ID': '企业微信CorpID',
        'WECHAT_APP_SECRET': '企业微信AppSecret',
        'WECHAT_AGENT_ID': '企业微信AgentID',
        'WECHAT_MESSAGE_TOKEN': '企业微信消息Token',
        'WECHAT_ENCODING_AES_KEY': '企业微信EncodingAESKey',
        'SECRET_KEY': 'Django密钥',
    }
    
    missing_vars = []
    for var_name, description in required_vars.items():
        value = os.environ.get(var_name, '')
        if value:
            masked_value = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            print_success(f"{var_name} ({description}): 已设置 ({masked_value})")
        else:
            print_error(f"{var_name} ({description}): 未设置")
            missing_vars.append(var_name)
    
    if missing_vars:
        print_warning(f"缺少 {len(missing_vars)} 个关键环境变量")
        return False
    else:
        print_success("所有关键环境变量已设置")
        return True


def check_log_files():
    """检查日志文件"""
    print_header("5. 日志文件检查")
    
    log_files = {
        'Django错误日志': '/var/www/yuantong/logs/error.log',
        'Django日志': '/var/www/yuantong/logs/django.log',
        'Gunicorn错误日志': '/var/www/yuantong/logs/gunicorn_error.log',
        'Gunicorn访问日志': '/var/www/yuantong/logs/gunicorn_access.log',
        'Celery Beat日志': '/var/www/yuantong/logs/celery_beat.log',
        'Celery Worker日志': '/var/www/yuantong/logs/celery_worker.log',
    }
    
    for log_name, log_path in log_files.items():
        if os.path.exists(log_path):
            try:
                size = os.path.getsize(log_path)
                size_mb = size / (1024 * 1024)
                mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
                time_diff = (datetime.now() - mtime).total_seconds() / 3600
                
                if size_mb > 100:
                    print_warning(f"{log_name}: {size_mb:.2f}MB (文件较大，建议清理)")
                else:
                    print_success(f"{log_name}: {size_mb:.2f}MB")
                
                if time_diff > 24:
                    print_warning(f"  - 最后修改时间: {time_diff:.1f} 小时前")
                else:
                    print_info(f"  - 最后修改时间: {time_diff:.1f} 小时前")
            except Exception as e:
                print_error(f"{log_name}: 无法读取 ({str(e)})")
        else:
            print_warning(f"{log_name}: 文件不存在")


def check_disk_space():
    """检查磁盘空间"""
    print_header("6. 磁盘空间检查")
    
    try:
        result = subprocess.run(
            ['df', '-h', '/var/www/yuantong'],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 5:
                used_percent = int(parts[4].rstrip('%'))
                if used_percent > 90:
                    print_error(f"磁盘使用率: {parts[4]} (空间不足)")
                elif used_percent > 80:
                    print_warning(f"磁盘使用率: {parts[4]} (空间紧张)")
                else:
                    print_success(f"磁盘使用率: {parts[4]}")
                print_info(f"已用: {parts[2]}, 可用: {parts[3]}, 总计: {parts[1]}")
    except Exception as e:
        print_warning(f"无法检查磁盘空间: {str(e)}")


def check_recent_errors():
    """检查最近的错误"""
    print_header("7. 最近错误检查")
    
    error_log = '/var/www/yuantong/logs/error.log'
    if os.path.exists(error_log):
        try:
            with open(error_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                error_lines = [line for line in lines[-50:] if 'ERROR' in line or 'Exception' in line]
                
                if error_lines:
                    print_warning(f"发现 {len(error_lines)} 条最近的错误日志")
                    print_info("最近5条错误:")
                    for line in error_lines[-5:]:
                        print(f"  {line.strip()[:150]}")
                else:
                    print_success("最近50行日志中没有发现错误")
        except Exception as e:
            print_warning(f"无法读取错误日志: {str(e)}")
    else:
        print_warning("错误日志文件不存在")


def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("系统健康检查")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print(f"{Colors.END}\n")
    
    results = {
        'django': check_django_service(),
        'celery': check_celery_services(),
        'database': check_database(),
        'environment': check_environment_variables(),
    }
    
    check_log_files()
    check_disk_space()
    check_recent_errors()
    
    # 总结
    print_header("检查总结")
    
    all_ok = all(results.values())
    
    if all_ok:
        print_success("所有关键服务运行正常！")
        return 0
    else:
        print_error("部分服务存在问题，请检查上述错误信息")
        failed_services = [name for name, ok in results.items() if not ok]
        print_warning(f"有问题的服务: {', '.join(failed_services)}")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(130)
    except Exception as e:
        print_error(f"检查过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

