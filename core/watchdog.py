"""Watchdog 守护进程 — 监控Agent健康，防止自毁"""
import os
import time
import hashlib
import threading
import psutil


class Watchdog:
    """独立守护进程，监控Agent运行状态和宪法完整性"""

    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.constitution_path = None
        self.agent_pid = None
        self._running = False
        self._thread = None
        self._last_constitution_hash = None
        self._alerts = []

    @property
    def running(self) -> bool:
        return self._running

    def start(self):
        """启动守护"""
        if self.constitution_path is None:
            self.constitution_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "constitution.md"
            )
        if os.path.exists(self.constitution_path):
            self._last_constitution_hash = self._hash_file(self.constitution_path)

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止守护"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        """守护循环"""
        while self._running:
            try:
                # 检查宪法完整性
                constitution_issues = self._check_constitution()
                if constitution_issues:
                    self._alerts.extend(constitution_issues)

                # 检查Agent进程
                if self.agent_pid:
                    if not self._check_process(self.agent_pid):
                        self._alerts.append(f"Agent进程(pid={self.agent_pid})已停止")

            except Exception as e:
                self._alerts.append(f"Watchdog检查异常: {e}")

            time.sleep(self.check_interval)

    def _check_constitution(self) -> list:
        """检查宪法文件是否被篡改"""
        issues = []
        if not os.path.exists(self.constitution_path):
            issues.append("⚠️ 宪法文件丢失！")
            return issues

        current_hash = self._hash_file(self.constitution_path)
        if self._last_constitution_hash and current_hash != self._last_constitution_hash:
            issues.append("⚠️ 宪法文件被修改！")
            self._last_constitution_hash = current_hash

        return issues

    def _check_process(self, pid: int) -> bool:
        """检查进程是否存活"""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

    def _hash_file(self, path: str) -> str:
        """计算文件SHA-256"""
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def get_health_report(self) -> dict:
        """获取健康报告"""
        status = "healthy"
        if self._alerts:
            status = "warning"
        return {
            "status": status,
            "running": self._running,
            "constitution_ok": len(self._check_constitution()) == 0,
            "alerts": self._alerts[-10:],
        }

    def get_alerts(self) -> list:
        """获取并清空告警"""
        alerts = self._alerts.copy()
        self._alerts.clear()
        return alerts
