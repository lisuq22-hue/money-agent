"""系统操作模块 — Agent像真人一样管理服务器"""
import os
import shutil
import subprocess
import time
import glob
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class SystemOps:
    """Agent的服务器操作能力"""

    project_dir: str
    data_dir: str
    logs_dir: str
    max_log_age_days: int = 7
    max_log_size_mb: int = 100

    # === 资源采集 ===

    def get_real_cpu(self) -> float:
        """真实CPU使用率"""
        if HAS_PSUTIL:
            return psutil.cpu_percent(interval=1)
        return 0.0

    def get_real_memory_mb(self) -> float:
        """真实内存使用 (MB)"""
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            return mem.used / 1024 / 1024
        return 0.0

    def get_real_disk_gb(self) -> float:
        """真实磁盘使用 (GB)"""
        if HAS_PSUTIL:
            usage = psutil.disk_usage(self.project_dir)
            return usage.used / 1024 / 1024 / 1024
        return 0.0

    def get_process_count(self) -> int:
        """当前运行的进程数"""
        if HAS_PSUTIL:
            return len(psutil.pids())
        return 0

    def get_my_processes(self) -> list[dict]:
        """获取Agent自己的进程信息"""
        my_procs = []
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    if info['name'] and 'python' in info['name'].lower():
                        mem_mb = info.get('memory_info')
                        my_procs.append({
                            'pid': info['pid'],
                            'cpu': info.get('cpu_percent', 0),
                            'memory_mb': (mem_mb.rss / 1024 / 1024) if mem_mb else 0,
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return my_procs

    def kill_runaway_process(self, pid: int) -> bool:
        """杀死失控进程"""
        try:
            if HAS_PSUTIL:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)
                return True
        except Exception:
            try:
                os.kill(pid, 9)  # SIGKILL on Unix
            except Exception:
                pass
        return False

    # === 磁盘清理 ===

    def clean_old_logs(self) -> int:
        """清理过期日志，返回删除的文件数"""
        count = 0
        cutoff = time.time() - self.max_log_age_days * 86400
        log_patterns = [
            os.path.join(self.logs_dir, '*.log'),
            os.path.join(self.logs_dir, '*.txt'),
        ]

        for pattern in log_patterns:
            for f in glob.glob(pattern):
                try:
                    if os.path.getmtime(f) < cutoff:
                        os.remove(f)
                        count += 1
                except OSError:
                    pass

        return count

    def split_large_logs(self) -> int:
        """分割过大的日志文件"""
        count = 0
        max_bytes = self.max_log_size_mb * 1024 * 1024
        for f in glob.glob(os.path.join(self.logs_dir, '*.log')):
            try:
                if os.path.getsize(f) > max_bytes:
                    backup = f + f'.{int(time.time())}.old'
                    shutil.move(f, backup)
                    count += 1
            except OSError:
                pass
        return count

    def clean_temp_files(self) -> int:
        """清理Python缓存和临时文件"""
        count = 0
        for root, dirs, files in os.walk(self.project_dir):
            for d in dirs:
                if d == '__pycache__' or d.endswith('.egg-info'):
                    try:
                        shutil.rmtree(os.path.join(root, d))
                        count += 1
                    except OSError:
                        pass
            for f in files:
                if f.endswith('.pyc') or f.endswith('.pyo'):
                    try:
                        os.remove(os.path.join(root, f))
                        count += 1
                    except OSError:
                        pass
        return count

    def check_disk_space(self) -> dict:
        """检查磁盘空间，返回可用空间和清理建议"""
        gb = self.get_real_disk_gb()
        total = 0
        if HAS_PSUTIL:
            total = psutil.disk_usage(self.project_dir).total / 1024 / 1024 / 1024

        return {
            'used_gb': round(gb, 1),
            'total_gb': round(total, 1),
            'free_gb': round(total - gb, 1),
            'need_cleanup': gb > 30,
            'critical': gb > 35,
        }

    def auto_cleanup(self) -> dict:
        """智能自动清理，返回清理报告"""
        report = {
            'old_logs_deleted': 0,
            'logs_split': 0,
            'temp_files_cleaned': 0,
            'disk_before_gb': self.get_real_disk_gb(),
        }

        disk = self.check_disk_space()
        if disk['need_cleanup']:
            report['old_logs_deleted'] = self.clean_old_logs()
            report['logs_split'] = self.split_large_logs()
            report['temp_files_cleaned'] = self.clean_temp_files()

        report['disk_after_gb'] = self.get_real_disk_gb()
        report['freed_gb'] = round(report['disk_before_gb'] - report['disk_after_gb'], 2)
        return report

    # === 包管理 ===

    def install_package(self, package: str, manager: str = 'pip') -> dict:
        """安装Python包"""
        try:
            result = subprocess.run(
                [manager, 'install', package],
                capture_output=True, text=True, timeout=120,
                cwd=self.project_dir,
            )
            return {
                'success': result.returncode == 0,
                'package': package,
                'output': result.stdout[-500:] + result.stderr[-200:],
            }
        except Exception as e:
            return {'success': False, 'package': package, 'error': str(e)}

    def check_package_installed(self, package: str) -> bool:
        """检查包是否已安装"""
        try:
            __import__(package.replace('-', '_'))
            return True
        except ImportError:
            return False

    def install_requirements(self) -> dict:
        """安装requirements.txt中的依赖"""
        req_path = os.path.join(self.project_dir, 'requirements.txt')
        if not os.path.exists(req_path):
            return {'success': False, 'error': 'requirements.txt not found'}

        result = subprocess.run(
            ['pip', 'install', '-r', req_path],
            capture_output=True, text=True, timeout=300,
            cwd=self.project_dir,
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout[-500:] + result.stderr[-200:],
        }

    # === 系统命令 ===

    def run_shell(self, command: str, timeout: int = 60) -> dict:
        """执行shell命令（受限）"""
        # 安全：禁止危险命令
        dangerous = ['rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:', '> /dev/sda']
        for d in dangerous:
            if d in command:
                return {'success': False, 'error': f'危险命令被拦截: {d}'}

        try:
            result = subprocess.run(
                command, shell=True,
                capture_output=True, text=True, timeout=timeout,
                cwd=self.project_dir,
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout[-1000:],
                'stderr': result.stderr[-500:],
                'exit_code': result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': f'命令超时 ({timeout}s)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # === 进程管理 ===

    def start_background_task(self, script: str, name: str = '') -> dict:
        """启动后台任务"""
        try:
            proc = subprocess.Popen(
                ['python', script],
                cwd=self.project_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return {'success': True, 'pid': proc.pid, 'name': name or script}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_process_running(self, pid: int) -> bool:
        """检查进程是否在运行"""
        if HAS_PSUTIL:
            try:
                return psutil.Process(pid).is_running()
            except psutil.NoSuchProcess:
                return False
        return False

    def get_health_report(self) -> dict:
        """完整健康报告"""
        cpu = self.get_real_cpu()
        mem = self.get_real_memory_mb()
        disk = self.get_real_disk_gb()

        return {
            'timestamp': time.time(),
            'cpu_percent': cpu,
            'memory_mb': round(mem, 0),
            'disk_gb': round(disk, 1),
            'process_count': self.get_process_count(),
            'my_processes': len(self.get_my_processes()),
            'healthy': cpu < 70 and mem < 1200 and disk < 30,
            'warnings': self._get_warnings(cpu, mem, disk),
        }

    def _get_warnings(self, cpu: float, mem: float, disk: float) -> list:
        warnings = []
        if cpu > 70:
            warnings.append(f'CPU使用率 {cpu:.0f}%（警戒70%）')
        if mem > 1200:
            warnings.append(f'内存使用 {mem:.0f}MB（警戒1200MB）')
        if disk > 30:
            warnings.append(f'磁盘使用 {disk:.1f}GB（警戒30GB）')
        return warnings
