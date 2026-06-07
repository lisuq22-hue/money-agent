# tests/test_pipeline.py
import os
import tempfile
import pytest
from agent.pipeline import Pipeline


class TestPipeline:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pipeline = Pipeline(
            project_dir=self.tmpdir,
            data_dir=os.path.join(self.tmpdir, "data"),
        )

    def test_pipeline_has_required_steps(self):
        """流水线应包含所有必要步骤"""
        steps = self.pipeline.get_steps()
        step_orders = [s["order"] for s in steps]
        assert len(steps) == 16, f"应有16步，实际{len(steps)}步"
        assert step_orders == list(range(1, 17)), "步骤顺序应为1-16"

    def test_pipeline_dry_run(self):
        """干跑模式不应执行实际操作"""
        results = self.pipeline.run(dry_run=True)
        assert isinstance(results, dict)
        assert results["mode"] == "dry_run"

    def test_pre_run_check(self):
        """运行前检查应验证必要条件"""
        checks = self.pipeline.pre_run_checks()
        assert isinstance(checks, dict)
        assert len(checks) > 0
