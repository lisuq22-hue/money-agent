"""进化引擎 — Agent读代码、写代码、测试、提交的核心"""
import os
import re
import subprocess
import time
from dataclasses import dataclass, field


@dataclass
class EvolveEngine:
    """Agent的自我进化引擎"""

    project_dir: str
    feature_branch_prefix: str = "evolve"

    _current_branch: str = ""
    _session_tasks: list = field(default_factory=list)

    def prepare_session(self, targets: list) -> list:
        """准备一次进化会话，返回任务列表"""
        self._session_tasks = self._generate_session_plan(targets)
        return self._session_tasks

    def execute_task(self, task: dict, ai_coder) -> dict:
        """执行单个进化任务

        ai_coder: 函数，接收prompt返回生成的代码
        返回: {"success": bool, "task": dict, "output": str}
        """
        task_id = task.get("id", "unknown")
        description = task.get("description", task.get("title", ""))

        try:
            # 1. 创建feature分支
            branch = self._make_branch_name(description)
            self._run_git(["checkout", "-b", branch])
            self._current_branch = branch

            # 2. 让AI写代码
            code_prompt = self._make_code_prompt(task)
            code = ai_coder(code_prompt)

            # 3. AI写的代码保存到文件
            self._apply_changes(code, task)

            # 4. 测试
            test_result = self._run_tests()
            if not test_result["passed"]:
                # 最多重试3次
                for attempt in range(3):
                    fix_prompt = self._make_fix_prompt(code, test_result["output"])
                    fixed_code = ai_coder(fix_prompt)
                    self._apply_changes(fixed_code, task)
                    test_result = self._run_tests()
                    if test_result["passed"]:
                        break

            if test_result["passed"]:
                # 5. 提交
                self._run_git(["add", "-A"])
                self._run_git(["commit", "-m",
                    f"evolve: {description}\n\nTask: {task_id}\n"
                    f"Co-Authored-By: MoneyAgent <agent@moneyagent.dev>"])
                self._run_git(["checkout", "main"])
                self._run_git(["merge", branch, "--no-ff", "-m",
                    f"merge: {description}"])
                self._run_git(["branch", "-d", branch])

                return {"success": True, "task": task, "output": "进化成功"}
            else:
                # 失败回退
                self._run_git(["checkout", "main"])
                self._run_git(["branch", "-D", branch])
                return {
                    "success": False,
                    "task": task,
                    "output": f"测试失败:\n{test_result['output'][:500]}"
                }
        except Exception as e:
            return {"success": False, "task": task, "output": str(e)}

    def _make_branch_name(self, description: str) -> str:
        """生成分支名"""
        safe_name = re.sub(r'[^\w一-鿿-]', '-', description)[:50]
        timestamp = int(time.time())
        return f"{self.feature_branch_prefix}/{timestamp}-{safe_name}"

    def _generate_session_plan(self, targets: list) -> list:
        """生成会话计划"""
        tasks = []
        for i, target in enumerate(targets):
            if isinstance(target, dict):
                title = target.get("title", f"任务{i+1}")
                description = target.get("body", target.get("description", ""))
            else:
                title = str(target)
                description = str(target)

            tasks.append({
                "id": f"task-{i+1:03d}",
                "title": title[:100],
                "description": description[:500],
                "status": "pending",
            })
        return tasks[:3]  # 每轮最多3个任务

    def _make_code_prompt(self, task: dict) -> str:
        """生成编程提示词"""
        return (
            f"你需要完成以下任务，修改 {self.project_dir} 中的代码：\n\n"
            f"## 任务\n{task.get('title')}\n\n"
            f"## 详细描述\n{task.get('description')}\n\n"
            f"## 要求\n"
            f"1. 只能修改 agent/ 和 plugins/ 下的文件\n"
            f"2. 不能修改 core/ 下的任何文件\n"
            f"3. 不能修改 constitution.md\n"
            f"4. 代码必须包含测试\n"
            f"5. 不能泄露任何敏感信息\n\n"
            f"请只输出需要修改的代码，每段代码前标注文件路径。"
        )

    def _make_fix_prompt(self, original_code: str, test_output: str) -> str:
        """生成修复提示词"""
        return (
            f"以下代码的测试失败了，请修复：\n\n"
            f"## 原始代码\n{original_code[:2000]}\n\n"
            f"## 测试输出\n{test_output[:1000]}\n\n"
            f"请只输出修复后的代码，标注文件路径。"
        )

    def _apply_changes(self, code: str, task: dict):
        """把AI生成的代码应用到文件"""
        current_file = None
        current_content = []

        for line in code.split("\n"):
            file_match = re.match(r'^[#/]{2,4}\s*(?:文件[：:]?\s*)?([a-zA-Z0-9_/.-]+\.py)', line)
            if file_match:
                if current_file and current_content:
                    self._write_file(current_file, "\n".join(current_content))
                current_file = os.path.join(self.project_dir, file_match.group(1))
                current_content = []
            elif current_file:
                current_content.append(line)

        if current_file and current_content:
            self._write_file(current_file, "\n".join(current_content))

    def _write_file(self, path: str, content: str):
        """写入文件（安全检查：不能写core/目录）"""
        rel_path = os.path.relpath(path, self.project_dir)
        if rel_path.startswith("core/") or rel_path == "constitution.md":
            raise PermissionError(f"安全规则禁止修改: {rel_path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _run_tests(self) -> dict:
        """运行测试"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "passed": result.returncode == 0,
                "output": result.stdout[-2000:] + result.stderr[-1000:],
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "output": "测试超时 (120s)"}
        except Exception as e:
            return {"passed": False, "output": str(e)}

    def _run_git(self, args: list) -> str:
        """执行Git命令"""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 and "checkout" not in args:
            raise RuntimeError(f"Git命令失败: git {' '.join(args)}\n{result.stderr}")
        return result.stdout
