"""
重启 Celery Worker
"""
from django.core.management.base import BaseCommand
import subprocess
import os
import signal
import time


class Command(BaseCommand):
    help = '重启 Celery Worker 以重新加载任务'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('重启 Celery Worker'))
        self.stdout.write('='*60 + '\n')
        
        # 1. 查找 Worker 进程
        self.stdout.write('\n[1] 查找 Celery Worker 进程...')
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            worker_processes = [
                line for line in result.stdout.split('\n') 
                if 'celery' in line.lower() and 'worker' in line.lower() and 'beat' not in line.lower() and 'python' in line.lower()
            ]
            
            if worker_processes:
                # 提取进程ID（主进程）
                main_pids = []
                for proc in worker_processes:
                    parts = proc.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            # 检查是否是主进程（包含 "celery -A yuantong worker"）
                            if 'celery' in proc and '-A' in proc and 'worker' in proc:
                                main_pids.append(pid)
                                self.stdout.write(f'  找到进程: PID={pid}')
                        except (ValueError, IndexError):
                            pass
                
                if main_pids:
                    # 2. 停止 Worker 进程（发送 SIGTERM 给主进程，会优雅关闭所有子进程）
                    self.stdout.write(f'\n[2] 停止 Celery Worker 进程 (PID: {main_pids[0]})...')
                    try:
                        os.kill(main_pids[0], signal.SIGTERM)
                        self.stdout.write(self.style.SUCCESS('  ✅ 已发送停止信号'))
                        
                        # 等待进程退出（最多等待10秒）
                        for i in range(10):
                            time.sleep(1)
                            result = subprocess.run(
                                ['ps', '-p', str(main_pids[0])],
                                capture_output=True,
                                text=True
                            )
                            if result.returncode != 0:
                                break
                        else:
                            # 如果还在运行，强制终止
                            self.stdout.write(self.style.WARNING('  进程仍在运行，强制终止...'))
                            os.kill(main_pids[0], signal.SIGKILL)
                            time.sleep(1)
                        
                        self.stdout.write(self.style.SUCCESS('  ✅ Celery Worker 已停止'))
                    except ProcessLookupError:
                        self.stdout.write(self.style.SUCCESS('  ✅ 进程已停止'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ 停止失败: {str(e)}'))
                        return
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  未找到有效的Worker主进程'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  Celery Worker 进程未运行'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 查找进程失败: {str(e)}'))
            return
        
        # 3. 等待一下确保进程完全退出
        time.sleep(2)
        
        # 4. 启动新的 Worker 进程
        self.stdout.write('\n[3] 启动 Celery Worker...')
        try:
            base_dir = '/var/www/yuantong'
            celery_bin = os.path.join(base_dir, 'venv', 'bin', 'celery')
            env_file = os.path.join(base_dir, '.env.production')
            
            # 加载环境变量文件
            env = os.environ.copy()
            env['PATH'] = f"{os.path.join(base_dir, 'venv', 'bin')}:{env.get('PATH', '')}"
            
            # 读取 .env.production 文件并添加到环境变量
            if os.path.exists(env_file):
                from dotenv import load_dotenv
                load_dotenv(env_file, override=True)
                # 更新env字典
                for key, value in os.environ.items():
                    if key.startswith('WECHAT_') or key.startswith('DB_'):
                        env[key] = value
                self.stdout.write(self.style.SUCCESS(f'  ✓ 已加载环境变量文件: {env_file}'))
            
            # 切换到项目目录并启动
            cmd = [
                celery_bin,
                '-A', 'yuantong',
                'worker',
                '--loglevel=info',
                '--logfile=/var/www/yuantong/logs/celery_worker.log',
                '--pidfile=/var/www/yuantong/logs/celery_worker.pid',
                '--concurrency=3',
                '-Q', 'default',
                '--detach'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=base_dir,
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('  ✅ Celery Worker 启动成功'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ 启动失败: {result.stderr}'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 启动失败: {str(e)}'))
            return
        
        # 5. 验证
        self.stdout.write('\n[4] 验证 Worker 是否运行...')
        time.sleep(3)
        
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            worker_processes = [
                line for line in result.stdout.split('\n') 
                if 'celery' in line.lower() and 'worker' in line.lower() and 'beat' not in line.lower() and 'python' in line.lower()
            ]
            
            if worker_processes:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Celery Worker 正在运行 ({len(worker_processes)} 个进程)'))
                for proc in worker_processes[:3]:  # 只显示前3个
                    self.stdout.write(f'    {proc[:100]}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ Celery Worker 未运行'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 验证失败: {str(e)}'))
        
        # 6. 检查任务注册
        self.stdout.write('\n[5] 检查任务注册...')
        self.stdout.write('  等待几秒钟让Worker完全启动...')
        time.sleep(3)
        
        try:
            # 读取Worker日志的最后几行，查找任务注册信息
            log_file = '/var/www/yuantong/logs/celery_worker.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    registered_tasks = [line for line in recent_lines if 'registered' in line.lower()]
                    if registered_tasks:
                        self.stdout.write(self.style.SUCCESS('  ✅ 找到任务注册信息:'))
                        for line in registered_tasks[-3:]:
                            self.stdout.write(f'    {line.strip()[:100]}')
                    else:
                        self.stdout.write(self.style.WARNING('  ⚠️  日志中未找到任务注册信息，可能需要更多时间启动'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  检查日志失败: {str(e)}'))
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('重启完成')
        self.stdout.write('='*60 + '\n')
        self.stdout.write('\n提示: Celery Worker 已重启，它会重新加载所有任务。')
        self.stdout.write('请等待几秒钟后检查任务是否正常执行。\n')
