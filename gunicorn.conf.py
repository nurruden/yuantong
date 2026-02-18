# Gunicorn配置文件
import multiprocessing

# 服务器配置
bind = "127.0.0.1:8000"  # 保持与runserver相同的地址
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True

# 日志配置
accesslog = "/var/www/yuantong/logs/gunicorn_access.log"
errorlog = "/var/www/yuantong/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程管理
pidfile = "/var/www/yuantong/gunicorn.pid"
daemon = False
