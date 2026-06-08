# tests/test_network.py
import os
import tempfile
import pytest
from agent.network import NetworkManager


class TestNetworkManager:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        # 只用本地测试目标
        self.net = NetworkManager(
            project_dir=self.tmpdir,
            data_dir=os.path.join(self.tmpdir, 'data'),
        )
        # 用本地可达的目标替换
        self.net.targets = [
            {'name': 'Baidu', 'url': 'https://www.baidu.com', 'timeout': 5},
        ]

    def test_check_all_targets(self):
        results = self.net.check_all_targets()
        assert 'Baidu' in results
        assert 'reachable' in results['Baidu']

    def test_detect_proxy_needed(self):
        result = self.net.detect_proxy_needed()
        assert 'need_proxy' in result
        assert 'suggestion' in result

    def test_configure_and_clear_proxy(self):
        self.net.configure_proxy('http://localhost:8080')
        assert os.environ.get('HTTP_PROXY') == 'http://localhost:8080'
        self.net.clear_proxy()
        assert os.environ.get('HTTP_PROXY') is None

    def test_get_network_status(self):
        status = self.net.get_network_status()
        assert 'targets' in status
        assert 'proxy_needed' in status

    def test_get_network_report(self):
        report = self.net.get_network_report()
        assert '网络状态报告' in report or 'Network' in report

    def test_get_unreachable_targets(self):
        # 添加一个不可达的目标
        self.net.targets.append(
            {'name': 'Unreachable', 'url': 'https://192.0.2.1', 'timeout': 2}
        )
        self.net.check_all_targets()
        unreachable = self.net.get_unreachable_targets()
        assert isinstance(unreachable, list)
