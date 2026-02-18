"""
重启 Celery Beat
"""
from django.core.management.base import BaseCommand
import subprocess
import os
import signal


class Command(BaseCommand):
    help = '重启 Celery Beat 以重新加载任务'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('重启 Celery Beat'))
        self.stdout.write('='*60 + '\n')
        
        # 1. 查找 Beat 进程
        self.stdout.write('\n[1] 查找 Celery Beat 进程...')
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            beat_processes = [
                line for line in result.stdout.split('\n') 
                if 'celery' in line.lower() and 'beat' in line.lower() and 'python' in line.lower()
            ]
            
            if beat_processes:
                # 提取进程ID
                pids = []
                for proc in beat_processes:
                    parts = proc.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            pids.append(pid)
                            self.stdout.write(f'  找到进程: PID={pid}')
                        except (ValueError, IndexError):
                            pass
                
                if pids:
                    # 2. 停止 Beat 进程
                    self.stdout.write(f'\n[2] 停止 Celery Beat 进程 (PID: {pids[0]})...')
                    try:
                        os.kill(pids[0], signal.SIGTERM)
                        self.stdout.write(self.style.SUCCESS('  ✅ 已发送停止信号'))
                        
                        # 等待进程退出
                        import time
                        time.sleep(2)
                        
                        # 检查是否还在运行
                        result = subprocess.run(
                            ['ps', '-p', str(pids[0])],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            self.stdout.write(self.style.WARNING('  进程仍在运行，强制终止...'))
                            os.kill(pids[0], signal.SIGKILL)
                            time.sleep(1)
                        
                        self.stdout.write(self.style.SUCCESS('  ✅ Celery Beat 已停止'))
                    except ProcessLookupError:
                        self.stdout.write(self.style.SUCCESS('  ✅ 进程已停止'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ 停止失败: {str(e)}'))
                        return
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  未找到有效的进程ID'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  Celery Beat 进程未运行'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 查找进程失败: {str(e)}'))
            return
        
        # 3. 启动新的 Beat 进程
        self.stdout.write('\n[3] 启动 Celery Beat...')
        try:
            base_dir = '/var/www/yuantong'
            venv_python = os.path.join(base_dir, 'venv', 'bin', 'python3')
            celery_bin = os.path.join(base_dir, 'venv', 'bin', 'celery')
            
            # 切换到项目目录并启动
            cmd = [
                celery_bin,
                '-A', 'yuantong',
                'beat',
                '--loglevel=info',
                '--logfile=/var/www/yuantong/logs/celery_beat.log',
                '--pidfile=/var/www/yuantong/logs/celery_beat.pid',
                '--scheduler=django_celery_beat.schedulers:DatabaseScheduler',
                '--detach'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=base_dir,
                capture_output=True,
                text=True,
                env={**os.environ, 'PATH': f"{os.path.join(base_dir, 'venv', 'bin')}:{os.environ.get('PATH', '')}"}
            )
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('  ✅ Celery Beat 启动成功'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ 启动失败: {result.stderr}'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 启动失败: {str(e)}'))
            return
        
        # 4. 验证
        self.stdout.write('\n[4] 验证 Beat 是否运行...')
        import time
        time.sleep(2)
        
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            beat_processes = [
                line for line in result.stdout.split('\n') 
                if 'celery' in line.lower() and 'beat' in line.lower() and 'python' in line.lower()
            ]
            
            if beat_processes:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Celery Beat 正在运行 ({len(beat_processes)} 个进程)'))
                for proc in beat_processes:
                    self.stdout.write(f'    {proc[:100]}')
            else:
                self.stdout.write(self.style.ERROR('  ❌ Celery Beat 未运行'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 验证失败: {str(e)}'))
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('重启完成')
        self.stdout.write('='*60 + '\n')
        self.stdout.write('\n提示: Celery Beat 已重启，它会重新从数据库加载所有定时任务。')
        self.stdout.write('请等待几分钟后检查任务是否在正确的时间执行。\n')


