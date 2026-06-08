# tests/test_system_ops.py
import os
import tempfile
import pytest
from agent.system_ops import SystemOps


class TestSystemOps:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sys = SystemOps(
            project_dir=self.tmpdir,
            data_dir=os.path.join(self.tmpdir, 'data'),
            logs_dir=os.path.join(self.tmpdir, 'logs'),
        )
        os.makedirs(self.sys.logs_dir, exist_ok=True)

    def test_get_health_report(self):
        health = self.sys.get_health_report()
        assert 'cpu_percent' in health
        assert 'memory_mb' in health
        assert 'disk_gb' in health
        assert 'healthy' in health

    def test_check_disk_space(self):
        disk = self.sys.check_disk_space()
        assert 'used_gb' in disk
        assert 'free_gb' in disk

    def test_install_package_safe(self):
        """测试安装一个安全的小包"""
        result = self.sys.install_package('six', manager='pip')
        assert 'success' in result

    def test_shell_command_safe(self):
        result = self.sys.run_shell('echo hello', timeout=5)
        assert result['success'] is True

    def test_shell_command_dangerous_blocked(self):
        result = self.sys.run_shell('rm -rf /')
        assert result['success'] is False
        assert '危险命令' in result.get('error', '')

    def test_auto_cleanup(self):
        report = self.sys.auto_cleanup()
        assert 'disk_before_gb' in report
        assert 'disk_after_gb' in report

    def test_process_count(self):
        count = self.sys.get_process_count()
        assert count > 0  # 至少有自己的进程

    def test_clean_old_logs(self):
        # 创建一个旧日志
        old_log = os.path.join(self.sys.logs_dir, 'old.log')
        with open(old_log, 'w') as f:
            f.write('test')
        os.utime(old_log, (0, 0))  # 设置为1970年
        count = self.sys.clean_old_logs()
        assert count >= 0
