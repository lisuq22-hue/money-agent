# tests/test_resource_monitor.py
import pytest
from core.resource_monitor import ResourceMonitor, ResourceStatus


class TestResourceMonitor:
    def setup_method(self):
        self.monitor = ResourceMonitor(
            cpu_warning=70.0,
            cpu_critical=90.0,
            memory_warning_mb=1200,
            memory_critical_mb=1600,
            disk_warning_gb=30.0,
            disk_critical_gb=35.0,
        )

    def test_normal_status(self):
        """正常资源使用应返回 OK"""
        status = self.monitor.check(cpu_percent=25.0, memory_mb=470, disk_gb=5.0)
        assert status == ResourceStatus.OK

    def test_cpu_warning(self):
        """CPU超过警告线应返回 WARNING"""
        status = self.monitor.check(cpu_percent=75.0, memory_mb=470, disk_gb=5.0)
        assert status == ResourceStatus.WARNING

    def test_cpu_critical(self):
        """CPU超过熔断线应返回 CRITICAL"""
        status = self.monitor.check(cpu_percent=92.0, memory_mb=470, disk_gb=5.0)
        assert status == ResourceStatus.CRITICAL

    def test_memory_critical(self):
        """内存超过熔断线应返回 CRITICAL"""
        status = self.monitor.check(cpu_percent=25.0, memory_mb=1700, disk_gb=5.0)
        assert status == ResourceStatus.CRITICAL

    def test_disk_warning(self):
        """磁盘超过警告线应返回 WARNING"""
        status = self.monitor.check(cpu_percent=25.0, memory_mb=470, disk_gb=32.0)
        assert status == ResourceStatus.WARNING

    def test_get_report(self):
        """应返回格式化的资源报告"""
        self.monitor.check(cpu_percent=45.0, memory_mb=800, disk_gb=10.0)
        report = self.monitor.get_report()
        assert "CPU" in report
        assert "45" in report
        assert "800" in report
