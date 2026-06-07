# tests/test_watchdog.py
import os
import time
import tempfile
import pytest
from core.watchdog import Watchdog


class TestWatchdog:
    def setup_method(self):
        self.watchdog = Watchdog(check_interval=0.1)

    def test_watchdog_starts_and_stops(self):
        """Watchdog应能正常启动和停止"""
        self.watchdog.start()
        assert self.watchdog.running is True
        self.watchdog.stop()
        assert self.watchdog.running is False

    def test_watchdog_detects_constitution_change(self, tmp_path):
        """检测宪法文件被修改时应报警"""
        const_path = tmp_path / "constitution.md"
        const_path.write_text("# Agent 宪法\n\n安全准则", encoding="utf-8")

        self.watchdog.constitution_path = str(const_path)
        self.watchdog._last_constitution_hash = "different_hash"

        issues = self.watchdog._check_constitution()
        assert len(issues) > 0

    def test_watchdog_checks_process_alive(self):
        """应能检查目标进程是否存活"""
        alive = self.watchdog._check_process(os.getpid())
        assert alive is True

    def test_watchdog_checks_nonexistent_process(self):
        """不存在的进程应返回False"""
        alive = self.watchdog._check_process(99999)
        assert alive is False

    def test_watchdog_get_health_report(self):
        """应返回健康报告"""
        self.watchdog.start()
        time.sleep(0.2)
        report = self.watchdog.get_health_report()
        assert "status" in report
        self.watchdog.stop()
