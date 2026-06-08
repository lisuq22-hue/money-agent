# tests/test_integration.py
import os
import sys
import pytest


class TestFullIntegration:
    """端到端集成测试"""

    def test_project_structure_complete(self):
        """验证项目文件结构完整"""
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        required_files = [
            "constitution.md",
            ".env.example",
            ".gitignore",
            "requirements.txt",
            "setup.bat",
            "run.bat",
            "core/__init__.py",
            "core/constitution.py",
            "core/crypto_utils.py",
            "core/privacy_filter.py",
            "core/resource_monitor.py",
            "core/safety_guard.py",
            "core/watchdog.py",
            "agent/__init__.py",
            "agent/main.py",
            "agent/pipeline.py",
            "agent/evolve_engine.py",
            "agent/memory.py",
            "agent/identity.py",
            "agent/ledger.py",
            "plugins/__init__.py",
            "plugins/base.py",
            "plugins/github_sponsors.py",
            "plugins/discovery.py",
            "utils/__init__.py",
            "utils/config.py",
            "utils/github_api.py",
            "utils/email_utils.py",
            "utils/notification.py",
        ]

        for path in required_files:
            full_path = os.path.join(project_dir, path)
            assert os.path.exists(full_path), f"缺少文件: {path}"

    def test_constitution_is_valid(self):
        """宪法文件必须有效"""
        from core.constitution import load_constitution, validate_constitution

        content = load_constitution()
        result = validate_constitution(content)
        assert result["valid"] is True, f"宪法不完整: {result['missing']}"

    def test_all_imports_work(self):
        """所有模块应能成功导入"""
        modules = [
            "core.constitution",
            "core.crypto_utils",
            "core.privacy_filter",
            "core.resource_monitor",
            "core.safety_guard",
            "core.watchdog",
            "agent.memory",
            "agent.identity",
            "agent.ledger",
            "agent.pipeline",
            "agent.evolve_engine",
            "plugins.base",
            "plugins.github_sponsors",
            "plugins.discovery",
            "utils.config",
            "utils.github_api",
            "utils.email_utils",
            "utils.notification",
        ]

        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"无法导入 {module_name}: {e}")

    def test_dry_run_works(self):
        """干跑模式应无报错"""
        import subprocess
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0,'.'); "
             "from core.constitution import load_constitution, validate_constitution; "
             "from agent.pipeline import Pipeline; "
             "p = Pipeline('.', 'data'); "
             "r = p.run(dry_run=True); "
             "print(r['message'])"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        assert "Traceback" not in output, f"干跑崩溃:\n{output}"

    def test_safety_guard_blocks_core_modification(self):
        """安全检查：Agent不能修改core/文件"""
        from core.safety_guard import SafetyGuard, SafetyViolation

        guard = SafetyGuard()
        with pytest.raises(SafetyViolation):
            guard.review_change({
                "file": "core/watchdog.py",
                "action": "modify",
                "content": "# disable watchdog",
            })

    def test_privacy_filter_works(self):
        """隐私过滤器正常工作"""
        from core.privacy_filter import PrivacyFilter

        pf = PrivacyFilter(user_phone="13800138000")
        result = pf.filter("我的手机是13800138000")
        assert "13800138000" not in result

    def test_ledger_profit_split(self):
        """账本三分天下计算正确"""
        import tempfile
        from agent.ledger import Ledger

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(data_dir=tmpdir)
            ledger.record_income("test", 90.00, "test", "test")
            split = ledger.get_profit_split()
            assert split["your_share"] == pytest.approx(30.00, rel=0.1)
            assert split["token_fund"] == pytest.approx(30.00, rel=0.1)
            assert split["freedom_fund"] == pytest.approx(30.00, rel=0.1)
