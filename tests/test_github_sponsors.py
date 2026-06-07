# tests/test_github_sponsors.py
import pytest
from plugins.github_sponsors import GitHubSponsorsPlugin


class TestGitHubSponsorsPlugin:
    def setup_method(self):
        self.plugin = GitHubSponsorsPlugin(
            name="github-sponsors",
            config={
                "github_token": "test_token",
                "repo_owner": "testuser",
                "repo_name": "test-repo",
            },
        )

    def test_plugin_initialized(self):
        assert self.plugin.name == "github-sponsors"
        assert self.plugin.enabled is True

    def test_disable_enable(self):
        self.plugin.disable()
        assert self.plugin.enabled is False
        self.plugin.enable()
        assert self.plugin.enabled is True

    def test_get_status_returns_dict(self):
        status = self.plugin.get_status()
        assert "name" in status
        assert "enabled" in status
        assert status["name"] == "github-sponsors"

    def test_work_plan_generation(self):
        """测试工作计划的生成（不调API）"""
        plan = self.plugin._generate_work_plan(
            issues=[],
            repo_status="active",
        )
        assert isinstance(plan, list)
