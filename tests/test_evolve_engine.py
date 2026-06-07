# tests/test_evolve_engine.py
import os
import tempfile
import pytest
from agent.evolve_engine import EvolveEngine


class TestEvolveEngine:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.engine = EvolveEngine(
            project_dir=self.tmpdir,
            feature_branch_prefix="test-evolve",
        )

    def test_creates_feature_branch_name(self):
        """应生成正确的feature分支名"""
        branch = self.engine._make_branch_name("添加新功能")
        assert branch.startswith("test-evolve/")
        assert "添加新功能" in branch

    def test_generates_session_plan(self):
        """应能读取目标并生成计划"""
        plan = self.engine._generate_session_plan(
            targets=["修复Bug #123", "优化README"]
        )
        assert len(plan) == 2
        assert any("Bug" in item.get("title", "") or "Bug" in item.get("description", "")
                   for item in plan)
