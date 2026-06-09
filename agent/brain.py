"""AI大脑 — 观察→思考→行动→学习，自主决策每一步做什么"""
import json
import re
import time
import os
import urllib.request
import urllib.error


AVAILABLE_ACTIONS = [
    {"name": "self_check", "desc": "检查系统资源和自身代码完整性", "cost": "low"},
    {"name": "evolve_code", "desc": "读取代码、发现问题、写代码改进自己", "cost": "high"},
    {"name": "explore_channels", "desc": "上网搜索新赚钱平台和机会", "cost": "medium"},
    {"name": "engage_community", "desc": "回复GitHub Issues/Discussions，维护社区", "cost": "medium"},
    {"name": "analyze_finance", "desc": "分析账本数据、计算ROI、优化赚钱策略", "cost": "low"},
    {"name": "learn", "desc": "总结近期赚钱和进化经验，沉淀到知识库", "cost": "low"},
    {"name": "register_platform", "desc": "用QQ邮箱注册发现的新平台账号", "cost": "high"},
    {"name": "cleanup", "desc": "清理过期日志、临时文件、释放磁盘空间", "cost": "low"},
    {"name": "rest", "desc": "当前无事可做，休息一会再观察", "cost": "none"},
]


class Brain:
    """Agent的AI大脑 — 每次循环自主决定下一步做什么"""

    def __init__(self, api_key: str, base_url: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = (base_url or "https://api.deepseek.com/v1").rstrip("/")
        self.model = model
        self._action_history = []

    def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """调用DeepSeek API (OpenAI兼容格式)"""
        if not self.api_key:
            raise RuntimeError("API key不可用")

        url = f"{self.base_url}/chat/completions"
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 300,
            "temperature": 0.7,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")[:200] if e.fp else ""
            raise RuntimeError(f"API {e.code}: {error_body}")
        except Exception as e:
            raise RuntimeError(f"API调用异常: {e}")

    def think(self, context: dict) -> dict:
        """
        输入当前状态，AI思考后返回行动决策

        返回: {"action": "xxx", "reason": "yyy", "urgency": 5, "rest_seconds": 300}
        """
        prompt = self._build_prompt(context)

        try:
            if self.api_key:
                ai_response = self._call_ai(self._system_prompt(), prompt)
                result = self._parse_response(ai_response)
            else:
                result = self._fallback_think(context)
        except Exception as e:
            print(f"  [Brain] AI调用失败: {e}，使用备用逻辑决策")
            result = self._fallback_think(context)

        self._action_history.append({
            "time": time.strftime("%H:%M"),
            "action": result.get("action", "unknown"),
            "reason": result.get("reason", ""),
        })
        if len(self._action_history) > 50:
            self._action_history = self._action_history[-50:]

        return result

    def _build_prompt(self, ctx: dict) -> str:
        recent = ctx.get("recent_actions", [])
        recent_str = "\n".join(
            f"  [{a.get('time', '?')}] {a.get('action', '?')} — {a.get('reason', '')}"
            for a in recent[-5:]
        ) or "无"

        return f"""你是MoneyAgent的决策大脑。分析现状，决定下一步行动。

## 当前状态
- 时间: {ctx.get('current_time', '?')}
- 系统: CPU {ctx['resources'].get('cpu', '?')}% | 内存 {ctx['resources'].get('memory_mb', '?')}MB | 磁盘 {ctx['resources'].get('disk_gb', '?')}GB
- GitHub可达: {ctx['network'].get('github_reachable', False)}
- 本月: 收入 ${ctx['finance'].get('income', 0):.2f} | 支出 ${ctx['finance'].get('expense', 0):.2f} | 利润 ${ctx['finance'].get('profit', 0):.2f}
- 知识库: {ctx.get('knowledge_count', 0)} 条经验
- 最近记忆: {ctx.get('memory_summary', '无')}

## 最近5次行动
{recent_str}

## 可选行动
{json.dumps(AVAILABLE_ACTIONS, ensure_ascii=False, indent=2)}

## 决策规则
- 资源紧张(CPU>50%或磁盘>25GB) → cleanup
- 本月收入为0且GitHub可达 → explore_channels 或 evolve_code
- 连续工作多轮 → rest
- 刚做过的事不重复
- 赚钱是核心使命

只返回JSON（不要其他内容）：
{{"action": "行动名", "reason": "简短理由", "urgency": 1-10, "rest_seconds": 建议休息秒数(60~7200)}}"""

    def _system_prompt(self) -> str:
        return """你是赚钱Agent的决策大脑。规则：
1. 安全第一 — 不能让服务器崩溃或泄露隐私
2. 赚钱优先 — 能增加收入的行动优先级最高
3. 持续进化 — 定期改进代码
4. 避免重复 — 不连续做相同的事
5. 按需休息 — 没事做就rest，但不要太久
只返回JSON，不要其他内容。"""

    def _parse_response(self, text: str) -> dict:
        match = re.search(r'\{[^{}]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return self._fallback_think({})

    def _fallback_think(self, ctx: dict) -> dict:
        """AI不可用时的备用决策"""
        recent_actions = [a.get("action") for a in self._action_history[-5:]]

        # 资源紧张 → 清理
        if ctx.get("resources", {}).get("disk_gb", 0) > 25:
            return {"action": "cleanup", "reason": "磁盘空间紧张", "urgency": 9, "rest_seconds": 60}

        # 本月没收入 → 优先探索
        if ctx.get("finance", {}).get("income", 0) == 0 and ctx.get("network", {}).get("github_reachable"):
            return {"action": "explore_channels", "reason": "本月尚未产生收入，积极寻找赚钱机会", "urgency": 8, "rest_seconds": 120}

        # 轮换策略：避免连续重复
        priority_rotation = ["self_check", "explore_channels", "learn", "evolve_code", "analyze_finance", "cleanup"]
        for action in priority_rotation:
            if action not in recent_actions[-2:]:
                reasons = {
                    "self_check": "例行系统自检",
                    "explore_channels": "寻找新赚钱平台",
                    "learn": "沉淀近期经验",
                    "evolve_code": "自我代码改进",
                    "analyze_finance": "分析财务数据优化策略",
                    "cleanup": "例行资源清理",
                }
                # 动态休息时间：越不紧迫，休息越久
                urgency_map = {
                    "self_check": 3, "explore_channels": 6, "learn": 4,
                    "evolve_code": 5, "analyze_finance": 3, "cleanup": 2,
                }
                rest_map = {
                    "self_check": 600, "explore_channels": 300, "learn": 900,
                    "evolve_code": 600, "analyze_finance": 1200, "cleanup": 1800,
                }
                return {
                    "action": action,
                    "reason": reasons.get(action, "常规任务"),
                    "urgency": urgency_map.get(action, 3),
                    "rest_seconds": rest_map.get(action, 300),
                }

        # 无事可做 → 休息
        return {"action": "rest", "reason": "近期任务已完成，短暂休息", "urgency": 1, "rest_seconds": 1800}

    def get_action_history(self) -> list:
        return self._action_history
