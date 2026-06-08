"""网络和代理管理 — Agent自主判断网络环境、配置代理、测试连通性"""
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class NetworkManager:
    """Agent的自主网络管理"""

    project_dir: str
    data_dir: str

    # 需要访问的目标列表
    targets: list = field(default_factory=lambda: [
        {'name': 'GitHub API', 'url': 'https://api.github.com', 'timeout': 10},
        {'name': 'Google', 'url': 'https://www.google.com', 'timeout': 10},
        {'name': 'Anthropic API', 'url': 'https://api.anthropic.com', 'timeout': 10},
        {'name': 'Baidu', 'url': 'https://www.baidu.com', 'timeout': 5},
    ])

    _proxy_config: Optional[str] = None
    _status_cache: dict = field(default_factory=dict)
    _last_check: float = 0

    # === 网络检测 ===

    def check_all_targets(self) -> dict:
        """检测所有目标平台的连通性"""
        results = {}
        for target in self.targets:
            results[target['name']] = self._check_single(target['url'], target['timeout'])

        self._status_cache = results
        self._last_check = time.time()
        return results

    def check_target(self, name: str) -> bool:
        """检测单个目标是否可达"""
        return self._status_cache.get(name, {}).get('reachable', False)

    def is_github_reachable(self) -> bool:
        return self.check_target('GitHub API')

    def is_anthropic_reachable(self) -> bool:
        return self.check_target('Anthropic API')

    def get_unreachable_targets(self) -> list:
        """获取所有不可达的目标"""
        return [name for name, r in self._status_cache.items() if not r.get('reachable', False)]

    # === 代理管理 ===

    def detect_proxy_needed(self) -> dict:
        """检测是否需要代理"""
        results = self.check_all_targets()
        overseas_unreachable = []
        domestic_reachable = results.get('Baidu', {}).get('reachable', False)

        for name, r in results.items():
            if name != 'Baidu' and not r.get('reachable', False):
                overseas_unreachable.append(name)

        return {
            'need_proxy': len(overseas_unreachable) > 0 and domestic_reachable,
            'overseas_blocked': overseas_unreachable,
            'domestic_ok': domestic_reachable,
            'suggestion': self._suggest_network_strategy(overseas_unreachable, domestic_reachable),
        }

    def configure_proxy(self, proxy_url: str) -> bool:
        """配置HTTP/HTTPS代理"""
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        self._proxy_config = proxy_url
        return True

    def clear_proxy(self):
        """清除代理设置"""
        for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            os.environ.pop(key, None)
        self._proxy_config = None

    def test_proxy(self, proxy_url: str) -> dict:
        """测试代理是否可用"""
        self.configure_proxy(proxy_url)
        results = {}
        for target in self.targets[:2]:  # 先测前两个
            results[target['name']] = self._check_single(target['url'], target['timeout'])
        return results

    def find_working_proxy(self, candidates: list[str]) -> Optional[str]:
        """从候选代理中找到可用的"""
        for proxy in candidates:
            if self.test_proxy(proxy).get('GitHub API', {}).get('reachable'):
                return proxy
        return None

    # === 网络状态监控 ===

    def get_network_status(self) -> dict:
        """获取完整网络状态"""
        status = self.check_all_targets()
        proxy = self.detect_proxy_needed()

        return {
            'timestamp': time.time(),
            'targets': status,
            'proxy_needed': proxy['need_proxy'],
            'proxy_active': self._proxy_config is not None,
            'proxy_config': self._proxy_config,
            'all_ok': all(r.get('reachable', False) for r in status.values()),
        }

    def get_network_report(self) -> str:
        """生成网络状态报告"""
        status = self.get_network_status()
        lines = ['网络状态报告:', f"时间: {time.strftime('%H:%M:%S')}"]

        for name, r in status['targets'].items():
            icon = 'OK' if r.get('reachable') else 'BLOCKED'
            latency = r.get('latency_ms', 0)
            lines.append(f"  [{icon}] {name} ({latency}ms)")

        if status['proxy_needed']:
            lines.append('检测到需要代理访问海外服务')
        if status['proxy_active']:
            lines.append(f'当前代理: {status["proxy_config"]}')

        return '\n'.join(lines)

    # === 内部 ===

    def _check_single(self, url: str, timeout: int) -> dict:
        """检测单个URL连通性"""
        start = time.time()
        try:
            if HAS_HTTPX:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.get(url)
                    elapsed = (time.time() - start) * 1000
                    return {
                        'reachable': resp.status_code < 500,
                        'status_code': resp.status_code,
                        'latency_ms': round(elapsed, 0),
                    }
            else:
                import urllib.request
                urllib.request.urlopen(url, timeout=timeout)
                elapsed = (time.time() - start) * 1000
                return {'reachable': True, 'latency_ms': round(elapsed, 0)}
        except Exception as e:
            return {
                'reachable': False,
                'error': str(e)[:100],
                'latency_ms': round((time.time() - start) * 1000, 0),
            }

    def _suggest_network_strategy(self, blocked: list, domestic_ok: bool) -> str:
        if not blocked:
            return '网络正常，无需代理'
        if domestic_ok:
            return f'国内网络正常，海外服务被屏蔽 ({", ".join(blocked)}) — 需要配置代理'
        return '网络异常 — 请检查服务器网络连接'
