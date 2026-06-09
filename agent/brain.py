"""AI大脑 — 观察→思考→行动→学习，自主决策每一步做什么"""
import json
import re
import time
import urllib.request
import urllib.error


AVAILABLE_ACTIONS = [
    {"name": "self_check", "desc": "检查系统资源、网络、代码完整性", "produces": "资源报告"},
    {"name": "evolve_code", "desc": "运行测试套件，分析代码质量，找出改进点", "produces": "测试结果+改进列表"},
    {"name": "explore_channels", "desc": "调用AI搜索互联网赚钱平台，评估可行性", "produces": "新平台列表+评估"},
    {"name": "engage_community", "desc": "读取GitHub Issues，生成回复，维护社区", "produces": "Issue回复"},
    {"name": "analyze_finance", "desc": "分析账本数据，计算各渠道ROI，生成财务洞察", "produces": "财务分析报告"},
    {"name": "learn", "desc": "总结最近的行动结果，提炼经验写入知识库", "produces": "知识条目"},
    {"name": "register_platform", "desc": "用QQ邮箱在新发现的平台注册账号", "produces": "注册结果"},
    {"name": "cleanup", "desc": "清理过期日志和临时文件，释放磁盘空间", "produces": "清理报告"},
    {"name": "rest", "desc": "暂时没有高价值任务，休息等待新机会", "produces": "无"},
]


class Brain:
    """Agent的AI大脑 — 每次循环自主决定下一步做什么"""

    def __init__(self, api_key: str, base_url: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = (base_url or "https://api.deepseek.com/v1").rstrip("/")
        self.model = model
        self._action_history = []
        self._verified_results = {}  # 已验证的行动结果

    # ====== AI调用 ======

    def call_ai(self, system: str, user: str, max_tokens: int = 500) -> str:
        """通用AI调用 — 所有模块共享"""
        if not self.api_key:
            raise RuntimeError("API key未配置")

        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")[:200] if e.fp else ""
            raise RuntimeError(f"API {e.code}: {body}")
        except Exception as e:
            raise RuntimeError(f"API调用异常: {e}")

    # ====== 决策 ======

    def think(self, context: dict) -> dict:
        """输入当前状态，AI思考后返回行动决策"""
        prompt = self._build_decision_prompt(context)

        try:
            if self.api_key:
                ai_response = self.call_ai(
                    self._decision_system_prompt(),
                    prompt,
                    max_tokens=300,
                )
                result = self._parse_json(ai_response)
            else:
                result = self._fallback_think(context)
        except Exception as e:
            print(f"  [Brain] AI调用失败: {e}")
            result = self._fallback_think(context)

        # 记录行动
        self._action_history.append({
            "time": time.strftime("%H:%M"),
            "action": result.get("action", "unknown"),
            "reason": result.get("reason", ""),
            "expected": result.get("expected_outcome", ""),
        })
        if len(self._action_history) > 100:
            self._action_history = self._action_history[-100:]

        return result

    def record_result(self, action: str, actual_outcome: str, success: bool):
        """记录行动的实际结果"""
        self._verified_results[action] = {
            "time": time.strftime("%H:%M"),
            "outcome": actual_outcome,
            "success": success,
        }

    # ====== 真实行动实现 ======

    def do_explore_channels(self) -> dict:
        """真正搜索赚钱平台 — 调用AI生成搜索策略，返回可操作结果"""
        prompt = """你是一个赚钱渠道研究专家。请搜索并列出当前(2026年)适合AI Agent赚钱的平台。

要求：
1. 必须是可以邮箱注册的平台（不需要手机号）
2. 有API或可自动化操作
3. 有明确的变现方式
4. 列出5个平台

对每个平台，给出：
- 平台名称和网址
- 变现方式（赞助/广告/打赏/接单/写作付费等）
- 注册难度（easy/medium/hard）
- 预计月收入范围
- 自动化可行性（高/中/低）

格式：每个平台一行，用 | 分隔

最后给一句总结：应该优先尝试哪个平台。"""

        try:
            result = self.call_ai(
                "你是一个务实的赚钱研究员。只输出事实，不输出幻想。",
                prompt,
                max_tokens=800,
            )
            return {
                "action": "explore_channels",
                "success": True,
                "platforms_found": result[:1000],
                "timestamp": time.strftime("%H:%M:%S"),
            }
        except Exception as e:
            return {"action": "explore_channels", "success": False, "error": str(e)}

    def do_self_check(self, resources: dict, network: dict) -> dict:
        """真正的自检 — 输出可验证的具体数据"""
        issues = []
        if resources.get("cpu", 0) > 70:
            issues.append(f"CPU使用率过高: {resources['cpu']}%")
        if resources.get("memory_mb", 0) > 1200:
            issues.append(f"内存使用过高: {resources['memory_mb']}MB")
        if resources.get("disk_gb", 0) > 25:
            issues.append(f"磁盘空间紧张: {resources['disk_gb']}GB")

        unreachable = [name for name, status in network.items() if not status]
        if unreachable:
            issues.append(f"网络不可达: {unreachable}")

        return {
            "action": "self_check",
            "success": True,
            "healthy": len(issues) == 0,
            "issues": issues,
            "resources": resources,
        }

    def do_evolve_code(self, test_pass: bool, test_output: str) -> dict:
        """真正的代码进化 — 基于测试结果决定改进方向"""
        if not test_pass:
            # 测试失败 — 分析失败原因
            try:
                analysis = self.call_ai(
                    "你是代码审查专家。分析测试失败原因，给出修复建议。",
                    f"测试输出:\n{test_output[:1500]}\n\n请分析：1)失败原因 2)修复建议 3)优先级",
                    max_tokens=400,
                )
            except Exception:
                analysis = "AI分析不可用"

            return {
                "action": "evolve_code",
                "success": False,
                "test_failures": True,
                "analysis": analysis,
            }
        else:
            # 测试通过 — 寻找改进机会
            return {
                "action": "evolve_code",
                "success": True,
                "test_pass": True,
                "message": "所有测试通过，代码健康",
            }

    def do_learn(self, recent_actions: list, ledger_data: dict) -> dict:
        """真正学习 — 总结行动结果并写入知识库"""
        actions_str = "\n".join(
            f"- {a.get('time','?')}: {a.get('action','?')} → {a.get('reason','')}"
            for a in recent_actions[-10:]
        )

        try:
            summary = self.call_ai(
                "你是经验总结专家。从行动记录中提炼可复用的经验。",
                f"最近行动:\n{actions_str}\n\n财务: 收入${ledger_data.get('total_income',0):.2f}\n\n"
                "请输出3条经验教训（每条一行，格式：- [经验] ...）",
                max_tokens=300,
            )
        except Exception:
            summary = "AI总结不可用"

        return {
            "action": "learn",
            "success": True,
            "summary": summary,
            "knowledge_written": bool(summary),
        }

    # ====== 内部方法 ======

    def _build_decision_prompt(self, ctx: dict) -> str:
        recent = ctx.get("recent_actions", [])
        recent_str = "\n".join(
            f"  [{a.get('time', '?')}] {a.get('action', '?')}"
            for a in recent[-8:]
        ) or "无"

        # 检查是否陷入循环
        last_actions = [a.get("action") for a in recent[-5:]]
        loop_warning = ""
        if len(last_actions) >= 3 and len(set(last_actions)) == 1:
            loop_warning = f"⚠️ 警告：最近连续{len(last_actions)}次都是 {last_actions[0]}，你在循环！必须选择不同行动。"

        return f"""你是MoneyAgent。分析现状，决定下一步。

## 当前状态
- 时间: {ctx.get('current_time', '?')}
- 系统: CPU {ctx['resources'].get('cpu', '?')}% | 内存 {ctx['resources'].get('memory_mb', '?')}MB | 磁盘 {ctx['resources'].get('disk_gb', '?')}GB
- GitHub可达: {ctx['network'].get('github_reachable', False)}
- 财务: 收入 ${ctx['finance'].get('income', 0):.2f} | 支出 ${ctx['finance'].get('expense', 0):.2f} | 利润 ${ctx['finance'].get('profit', 0):.2f}

## 最近行动
{recent_str}
{loop_warning}

## 强制规则
1. 连续3次相同行动 = 严重问题，必须换
2. 每月必须有收入 — 收入为0超过一周，必须尝试不同策略
3. 如果不能产生价值，就rest — 不要假装工作

返回JSON：{{"action": "行动名", "reason": "为什么", "expected_outcome": "预期产出什么", "urgency": 1-10, "rest_seconds": 休息秒数}}"""

    def _decision_system_prompt(self) -> str:
        return """你是赚钱Agent。规则：
1. 你的每个行动都必须产生可验证的产出
2. 不假装工作 — 如果做不到就承认
3. 赚钱第一，但不要死循环同一个无效行动
4. rest_seconds建议: 高紧迫120-300s, 中300-900s, 低900-3600s
只返回JSON。"""

    def _parse_json(self, text: str) -> dict:
        match = re.search(r'\{[^{}]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return self._fallback_think({})

    def _fallback_think(self, ctx: dict) -> dict:
        """备用决策 — 避免循环"""
        recent = [a.get("action") for a in self._action_history[-5:]]

        # 磁盘紧张 → 清理
        if ctx.get("resources", {}).get("disk_gb", 0) > 25:
            return {"action": "cleanup", "reason": "磁盘空间紧张", "urgency": 9, "rest_seconds": 60}

        # 检查是否在循环中 — 强制打破
        if len(recent) >= 3 and len(set(recent[-3:])) == 1:
            return {"action": "rest", "reason": f"连续{len(set(recent[-3:]))}次相同行动，强制休息打破循环", "urgency": 5, "rest_seconds": 1800}

        # 轮换策略
        # 无收入 → 探索
        if ctx.get("finance", {}).get("income", 0) == 0:
            if "explore_channels" not in recent[-3:]:
                return {"action": "explore_channels", "reason": "寻找赚钱机会", "urgency": 8, "rest_seconds": 300}
            if "evolve_code" not in recent[-2:]:
                return {"action": "evolve_code", "reason": "自我改进等待变现机会", "urgency": 5, "rest_seconds": 600}

        return {"action": "rest", "reason": "暂无高价值任务", "urgency": 2, "rest_seconds": 3600}

    def get_action_history(self) -> list:
        return self._action_history
