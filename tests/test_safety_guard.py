# tests/test_safety_guard.py
import pytest
from core.safety_guard import SafetyGuard, SafetyViolation


class TestSafetyGuard:
    def setup_method(self):
        self.guard = SafetyGuard()

    def test_allows_normal_code_change(self):
        """允许修改普通Python文件"""
        change = {
            "file": "agent/identity.py",
            "action": "modify",
            "content": "# 更新人格定义\nPERSONALITY = \"友好\"",
        }
        result = self.guard.review_change(change)
        assert result["allowed"] is True

    def test_blocks_constitution_modification(self):
        """阻止修改宪法文件"""
        change = {
            "file": "constitution.md",
            "action": "modify",
            "content": "删除安全准则",
        }
        with pytest.raises(SafetyViolation):
            self.guard.review_change(change)

    def test_blocks_core_file_modification(self):
        """阻止修改 core/ 目录下的文件"""
        change = {
            "file": "core/watchdog.py",
            "action": "modify",
            "content": "# 关闭watchdog",
        }
        with pytest.raises(SafetyViolation):
            self.guard.review_change(change)

    def test_blocks_secrets_deletion(self):
        """阻止删除 secrets 文件"""
        change = {
            "file": ".env",
            "action": "delete",
            "content": "",
        }
        with pytest.raises(SafetyViolation):
            self.guard.review_change(change)

    def test_blocks_git_directory_deletion(self):
        """阻止删除.git目录"""
        change = {
            "file": ".git/config",
            "action": "delete",
            "content": "",
        }
        with pytest.raises(SafetyViolation):
            self.guard.review_change(change)

    def test_blocks_privacy_leak(self):
        """阻止提交包含用户隐私数据的代码"""
        change = {
            "file": "agent/test.py",
            "action": "create",
            "content": "user_phone = '13800138000'",
        }
        with pytest.raises(SafetyViolation):
            self.guard.review_change(change)

    def test_allows_new_plugin(self):
        """允许在 plugins/ 下创建新文件"""
        change = {
            "file": "plugins/new_platform.py",
            "action": "create",
            "content": "# 新的赚钱模块\ndef earn(): pass",
        }
        result = self.guard.review_change(change)
        assert result["allowed"] is True
