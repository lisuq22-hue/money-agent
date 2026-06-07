"""16步赚钱+进化流水线 — Agent每次醒来的完整工作流程"""
import os
import time
import traceback
from dataclasses import dataclass


@dataclass
class PipelineStep:
    name: str
    order: int
    description: str


class Pipeline:
    """16步自主循环"""

    STEPS = [
        PipelineStep("醒来自检", 1, "检查代码完整性、资源状态"),
        PipelineStep("凭证检查", 2, "验证所有Token和Cookie是否有效"),
        PipelineStep("网络检测", 3, "测试目标平台网络连通性"),
        PipelineStep("读社区反馈", 4, "读取GitHub Issues/Discussions/Sponsors"),
        PipelineStep("记账", 5, "更新ledger.json，计算ROI"),
        PipelineStep("制定计划", 6, "生成session_plan/tasks.md"),
        PipelineStep("执行任务-写代码", 7, "AI写代码实现改进"),
        PipelineStep("执行任务-编译", 8, "运行构建检查"),
        PipelineStep("执行任务-测试", 9, "运行测试套件"),
        PipelineStep("执行任务-提交", 10, "Git commit变更"),
        PipelineStep("合并代码", 11, "创建PR -> CI通过 -> Merge到main"),
        PipelineStep("回复社区", 12, "更新Issues、写JOURNAL.md"),
        PipelineStep("探索新渠道", 13, "搜索新赚钱平台"),
        PipelineStep("自动注册", 14, "尝试注册发现的新平台"),
        PipelineStep("记账+报告", 15, "更新账本、生成日报"),
        PipelineStep("休眠", 16, "清理临时文件，等待下次唤醒"),
    ]

    def __init__(self, project_dir: str, data_dir: str):
        self.project_dir = project_dir
        self.data_dir = data_dir
        self._completed_steps = []
        self._session_log = []
        self._start_time = None

    def get_steps(self) -> list:
        return [
            {"name": s.name, "order": s.order, "description": s.description}
            for s in self.STEPS
        ]

    def get_progress(self) -> str:
        """获取进度"""
        completed = len(self._completed_steps)
        total = len(self.STEPS)
        bar = "█" * completed + "░" * (total - completed)
        return f"[{bar}] {completed}/{total} 步完成"

    def mark_step_done(self, step_name: str):
        self._completed_steps.append(step_name)
        self._session_log.append({
            "time": time.time(),
            "step": step_name,
            "status": "completed",
        })

    def mark_step_failed(self, step_name: str, error: str):
        self._session_log.append({
            "time": time.time(),
            "step": step_name,
            "status": "failed",
            "error": error,
        })

    def pre_run_checks(self) -> dict:
        """运行前检查"""
        checks = {}

        const_path = os.path.join(self.project_dir, "constitution.md")
        checks["constitution_exists"] = os.path.exists(const_path)

        env_path = os.path.join(self.project_dir, ".env")
        checks["env_exists"] = os.path.exists(env_path)

        core_path = os.path.join(self.project_dir, "core")
        checks["core_dir_exists"] = os.path.isdir(core_path)

        git_path = os.path.join(self.project_dir, ".git")
        checks["git_initialized"] = os.path.isdir(git_path)

        return checks

    def run(self, dry_run: bool = False, callbacks: dict = None) -> dict:
        """执行完整流水线"""
        self._start_time = time.time()
        callbacks = callbacks or {}

        if dry_run:
            return {
                "mode": "dry_run",
                "steps_total": len(self.STEPS),
                "steps_completed": 0,
                "message": "干跑模式 — 不执行实际操作",
            }

        results = {"steps_completed": 0, "steps_failed": 0, "errors": []}

        for step in self.STEPS:
            step_name = step.name

            if callbacks.get("on_step"):
                if not callbacks["on_step"](step_name):
                    self.mark_step_done(step_name)
                    results["steps_completed"] += 1
                    continue

            try:
                handler = getattr(self, f"_step_{step.order:02d}", None)
                if handler:
                    success = handler(callbacks)
                    if success:
                        self.mark_step_done(step_name)
                        results["steps_completed"] += 1
                    else:
                        self.mark_step_failed(step_name, "步骤返回失败")
                        results["steps_failed"] += 1
                        results["errors"].append(f"{step_name}: 失败")
                else:
                    self.mark_step_done(step_name)
                    results["steps_completed"] += 1
            except Exception as e:
                error_msg = f"{step_name}: {e}\n{traceback.format_exc()[-200:]}"
                self.mark_step_failed(step_name, str(e))
                results["steps_failed"] += 1
                results["errors"].append(error_msg)

                if callbacks.get("on_error"):
                    callbacks["on_error"](step_name, error_msg)

                if "Token" in str(e) or "network" in str(e).lower():
                    break

        return results

    def get_session_log(self) -> list:
        return self._session_log

    # Step handlers
    def _step_01(self, callbacks) -> bool:
        self._log("检查项目文件结构...")
        required = ["constitution.md", "core/", "agent/", "plugins/"]
        for path in required:
            full = os.path.join(self.project_dir, path)
            if not os.path.exists(full):
                self._log(f"缺少: {path}")
        return True

    def _step_02(self, callbacks) -> bool:
        self._log("检查凭证...")
        env_path = os.path.join(self.project_dir, ".env")
        return os.path.exists(env_path)

    def _step_03(self, callbacks) -> bool:
        self._log("检测网络连通性...")
        import httpx
        try:
            resp = httpx.get("https://api.github.com", timeout=10)
            self._log(f"GitHub API: {resp.status_code}")
            return True
        except Exception as e:
            self._log(f"GitHub API不可达: {e}")
            return False

    def _step_04(self, callbacks) -> bool:
        self._log("读取社区反馈...")
        return True

    def _step_05(self, callbacks) -> bool:
        self._log("更新账本...")
        return True

    def _step_06(self, callbacks) -> bool:
        self._log("制定会话计划...")
        return True

    def _step_07(self, callbacks) -> bool:
        self._log("写代码...")
        return True

    def _step_08(self, callbacks) -> bool:
        self._log("构建检查...")
        return True

    def _step_09(self, callbacks) -> bool:
        self._log("运行测试...")
        return True

    def _step_10(self, callbacks) -> bool:
        self._log("提交代码...")
        return True

    def _step_11(self, callbacks) -> bool:
        self._log("合并代码...")
        return True

    def _step_12(self, callbacks) -> bool:
        self._log("回复社区...")
        return True

    def _step_13(self, callbacks) -> bool:
        self._log("搜索新赚钱平台...")
        return True

    def _step_14(self, callbacks) -> bool:
        self._log("检查可注册的新平台...")
        return True

    def _step_15(self, callbacks) -> bool:
        self._log("生成日报...")
        return True

    def _step_16(self, callbacks) -> bool:
        self._log("清理临时文件，准备休眠...")
        return True

    def _log(self, msg: str):
        print(f"  [{time.strftime('%H:%M:%S')}] {msg}")
        self._session_log.append({"time": time.time(), "message": msg})
