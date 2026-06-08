"""Watchdog 守护进程 — 监控Agent健康，主动防自毁，强制执行"""
import os
import sys
import time
import hashlib
import threading
import json
import psutil


# 受保护的核心文件列表（Agent绝对不能改）
PROTECTED_FILES = [
    'constitution.md',
    'core/constitution.py',
    'core/watchdog.py',
    'core/safety_guard.py',
    'core/resource_monitor.py',
    'core/privacy_filter.py',
    'core/crypto_utils.py',
]

# 资源硬限制
HARD_LIMITS = {
    'cpu_percent': 90,
    'memory_mb': 1600,
    'disk_gb': 35,
    'max_processes': 50,
}


class Watchdog:
    """独立守护进程 — 监控+强制+恢复"""

    def __init__(self, check_interval: float = 5.0, project_dir: str = None):
        self.check_interval = check_interval
        self.project_dir = project_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.constitution_path = os.path.join(self.project_dir, 'constitution.md')
        self.agent_pid = None
        self._running = False
        self._thread = None
        self._last_constitution_hash = None
        self._alerts = []
        self._incident_log_path = os.path.join(self.project_dir, 'data', 'watchdog_incidents.json')
        self._restore_source = os.path.join(self.project_dir, 'data', 'constitution.backup')
        self._core_hashes = {}

    @property
    def running(self) -> bool:
        return self._running

    def start(self):
        """启动守护"""
        # 备份宪法
        self._backup_constitution()
        # 记录核心文件hash
        self._hash_all_protected()
        # 记录宪法hash
        if os.path.exists(self.constitution_path):
            self._last_constitution_hash = self._hash_file(self.constitution_path)

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._log_incident('info', 'Watchdog started')

    def stop(self):
        """停止守护"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._log_incident('info', 'Watchdog stopped')

    def _loop(self):
        """守护循环 — 检测+执行"""
        while self._running:
            try:
                # 1. 宪法完整性检查
                self._guard_constitution()

                # 2. 核心文件完整性检查
                self._guard_core_files()

                # 3. 资源硬限制检查
                self._guard_resources()

                # 4. Agent进程存活检查
                self._guard_agent_process()

            except Exception as e:
                self._alerts.append(f"Watchdog异常: {e}")

            time.sleep(self.check_interval)

    # === 宪法守护 ===

    def _guard_constitution(self):
        """守卫宪法文件 — 被篡改则恢复"""
        if not os.path.exists(self.constitution_path):
            self._alerts.append("宪法文件丢失！尝试从备份恢复...")
            if self._restore_constitution():
                self._alerts.append("宪法已从备份恢复")
            else:
                self._alerts.append("宪法恢复失败！系统进入保护模式")
                self._enter_protection_mode()
            return

        current_hash = self._hash_file(self.constitution_path)
        if self._last_constitution_hash and current_hash != self._last_constitution_hash:
            self._alerts.append("检测到宪法被修改！自动恢复原版...")
            self._restore_constitution()
            self._last_constitution_hash = self._hash_file(self.constitution_path)

    # === 核心文件守护 ===

    def _guard_core_files(self):
        """守卫核心文件 — 被删或修改则告警"""
        for rel_path in PROTECTED_FILES:
            full_path = os.path.join(self.project_dir, rel_path)
            if not os.path.exists(full_path):
                self._alerts.append(f"核心文件丢失: {rel_path}")
                self._log_incident('critical', f'Protected file missing: {rel_path}')
            else:
                h = self._hash_file(full_path)
                if rel_path in self._core_hashes and h != self._core_hashes[rel_path]:
                    self._alerts.append(f"核心文件被修改: {rel_path}")
                    self._log_incident('warning', f'Protected file modified: {rel_path}')
                    self._core_hashes[rel_path] = h

    # === 资源守护 ===

    def _guard_resources(self):
        """守卫服务器资源 — 超限则强制干预"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().used / 1024 / 1024
            disk = psutil.disk_usage(self.project_dir).used / 1024 / 1024 / 1024

            # CPU熔断
            if cpu >= HARD_LIMITS['cpu_percent']:
                self._alerts.append(f"CPU熔断: {cpu:.0f}%")
                self._kill_heavy_processes()

            # 内存熔断
            if mem >= HARD_LIMITS['memory_mb']:
                self._alerts.append(f"内存熔断: {mem:.0f}MB")
                self._kill_heavy_processes()

            # 磁盘熔断
            if disk >= HARD_LIMITS['disk_gb']:
                self._alerts.append(f"磁盘熔断: {disk:.1f}GB")
                self._cleanup_disk()

            # 进程数限制
            my_procs = [p for p in psutil.process_iter(['name'])
                       if p.info['name'] and 'python' in p.info['name'].lower()]
            if len(list(my_procs)) > HARD_LIMITS['max_processes']:
                self._alerts.append(f"进程数超限: {len(list(my_procs))}")
        except Exception:
            pass

    # === Agent进程守护 ===

    def _guard_agent_process(self):
        """守卫Agent进程 — 挂了则尝试重启"""
        if self.agent_pid is None:
            return

        if not self._check_process(self.agent_pid):
            self._alerts.append(f"Agent进程(pid={self.agent_pid})已停止，尝试重启...")
            self._log_incident('warning', f'Agent process died: pid={self.agent_pid}')
            self._restart_agent()

    # === 强制措施 ===

    def _kill_heavy_processes(self):
        """杀死资源占用最高的Agent进程"""
        try:
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    if info['name'] and 'python' in info['name'].lower():
                        mem = info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0
                        procs.append((info['pid'], mem))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            procs.sort(key=lambda x: x[1], reverse=True)
            # 保留自己，杀最重的3个
            my_pid = os.getpid()
            killed = 0
            for pid, mem in procs:
                if pid != my_pid and killed < 3:
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        proc.wait(timeout=5)
                        killed += 1
                        self._log_incident('action', f'Killed heavy process: pid={pid}, mem={mem:.0f}MB')
                    except Exception:
                        try:
                            os.kill(pid, 9)
                        except Exception:
                            pass

            if killed > 0:
                self._alerts.append(f"已终止 {killed} 个异常进程")
        except Exception:
            pass

    def _cleanup_disk(self):
        """紧急磁盘清理"""
        import glob
        import shutil
        cleaned = 0
        for pattern in ['logs/*.log', 'logs/*.old', '**/__pycache__']:
            for f in glob.glob(os.path.join(self.project_dir, pattern), recursive=True):
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                        cleaned += 1
                    elif os.path.isdir(f):
                        shutil.rmtree(f)
                        cleaned += 1
                except OSError:
                    pass
        if cleaned > 0:
            self._log_incident('action', f'Cleaned {cleaned} files in emergency')

    def _restart_agent(self):
        """尝试重启Agent"""
        try:
            main_script = os.path.join(self.project_dir, 'agent', 'main.py')
            if os.path.exists(main_script):
                import subprocess
                proc = subprocess.Popen(
                    [sys.executable, '-m', 'agent.main'],
                    cwd=self.project_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.agent_pid = proc.pid
                self._alerts.append(f"Agent已重启 (pid={proc.pid})")
        except Exception as e:
            self._alerts.append(f"Agent重启失败: {e}")

    def _enter_protection_mode(self):
        """进入保护模式 — 暂停Agent，只保留Watchdog"""
        self._alerts.append("进入保护模式！Agent已暂停，等待用户介入")
        self._kill_heavy_processes()
        self._log_incident('critical', 'PROTECTION MODE activated')

    # === 宪法备份恢复 ===

    def _backup_constitution(self):
        """备份宪法"""
        if os.path.exists(self.constitution_path):
            import shutil
            shutil.copy2(self.constitution_path, self._restore_source)

    def _restore_constitution(self) -> bool:
        """从备份恢复宪法"""
        if os.path.exists(self._restore_source):
            import shutil
            shutil.copy2(self._restore_source, self.constitution_path)
            return True
        return False

    def _hash_all_protected(self):
        """计算所有受保护文件的hash"""
        for rel_path in PROTECTED_FILES:
            full_path = os.path.join(self.project_dir, rel_path)
            if os.path.exists(full_path):
                self._core_hashes[rel_path] = self._hash_file(full_path)

    # === 工具方法 ===

    def _check_process(self, pid: int) -> bool:
        try:
            return psutil.Process(pid).is_running()
        except psutil.NoSuchProcess:
            return False

    def _hash_file(self, path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def get_health_report(self) -> dict:
        status = "healthy"
        if len(self._alerts) >= 3:
            status = "critical"
        elif len(self._alerts) >= 1:
            status = "warning"

        constitution_issues = []
        if os.path.exists(self.constitution_path):
            current = self._hash_file(self.constitution_path)
            if self._last_constitution_hash and current != self._last_constitution_hash:
                constitution_issues.append("modified")

        return {
            "status": status,
            "running": self._running,
            "constitution_ok": len(constitution_issues) == 0,
            "alerts": self._alerts[-10:],
            "incidents": self._load_incidents()[-5:],
        }

    def get_alerts(self) -> list:
        alerts = self._alerts.copy()
        self._alerts.clear()
        return alerts

    def _log_incident(self, level: str, message: str):
        incidents = self._load_incidents()
        incidents.append({
            'time': time.time(),
            'level': level,
            'message': message,
        })
        # 只保留最近100条
        incidents = incidents[-100:]
        os.makedirs(os.path.dirname(self._incident_log_path), exist_ok=True)
        with open(self._incident_log_path, 'w', encoding='utf-8') as f:
            json.dump(incidents, f, ensure_ascii=False, indent=2)

    def _load_incidents(self) -> list:
        if os.path.exists(self._incident_log_path):
            with open(self._incident_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
