# AI大脑自主决策 — 实施计划

**目标:** 将Agent从"固定16步死循环"改造为"AI大脑观察→思考→行动→学习"的自主决策循环

**架构:** 新增 `agent/brain.py` 调用 DeepSeek API 做决策。保留 pipeline.py 为工具箱。重写 main.py 为 brain 驱动的动态循环。

**技术栈:** Python 3.12+, DeepSeek API (via Anthropic SDK), 现有模块不变

---

## Task 1: 创建 AI 大脑模块

**Files:** Create `agent/brain.py`, Create `tests/test_brain.py`

brain.py 核心逻辑：
- 收集当前状态(资源/网络/账本/记忆/最近行为/时间)
- 调用 DeepSeek API，传入状态，要求返回JSON格式的行动决策
- 解析AI返回的行动，执行，记录结果
- 动态决定下次思考时间

```python
# agent/brain.py — AI大脑，自主决策下一步行动
import json
import os
import time
from datetime import datetime

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


AVAILABLE_ACTIONS = [
    {"name": "self_check", "desc": "检查系统资源和自身代码完整性", "cost": "low"},
    {"name": "evolve_code", "desc": "读取代码、发现问题、写代码改进自己", "cost": "high"},
    {"name": "explore_channels", "desc": "上网搜索新赚钱平台和机会", "cost": "medium"},
    {"name": "engage_community", "desc": "回复GitHub Issues、Discussions，维护社区", "cost": "medium"},
    {"name": "analyze_finance", "desc": "分析账本数据、计算ROI、优化赚钱策略", "cost": "low"},
    {"name": "learn", "desc": "总结近期赚钱和进化经验，沉淀到知识库", "cost": "low"},
    {"name": "register_platform", "desc": "用QQ邮箱注册发现的新平台账号", "cost": "high"},
    {"name": "cleanup", "desc": "清理过期日志、临时文件、释放磁盘", "cost": "low"},
    {"name": "rest", "desc": "当前无事可做，休息一会再观察", "cost": "none"},
]


class Brain:
    """Agent的AI大脑 — 观察→思考→行动→学习"""

    def __init__(self, api_key: str, base_url: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = base_url or "https://api.deepseek.com/v1"
        self.model = model
        self._client = None
        self._action_history = []  # 最近行动记录
        self._last_rest_reason = ""

    def _get_client(self):
        if self._client is None and HAS_ANTHROPIC:
            self._client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def think(self, context: dict) -> dict:
        """
        输入当前状态，AI思考后返回行动决策
        
        context = {
            "resources": {"cpu": 0, "memory_mb": 500, "disk_gb": 5},
            "network": {"github_reachable": True, "google_reachable": False},
            "finance": {"income": 0, "expense": 0, "profit": 0},
            "recent_actions": [...],  # 最近5次行动
            "memory_summary": "...",
            "knowledge_count": 3,
            "current_time": "2026-06-09 10:00",
        }
        
        返回: {"action": "self_check", "reason": "...", "urgency": 5, "rest_seconds": 300}
        """
        prompt = self._build_prompt(context)
        
        try:
            client = self._get_client()
            if client:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    system=self._system_prompt(),
                    messages=[{"role": "user", "content": prompt}],
                )
                result = self._parse_response(response.content[0].text)
            else:
                result = self._fallback_think(context)
        except Exception as e:
            print(f"  [Brain] AI调用失败: {e}，使用备用逻辑")
            result = self._fallback_think(context)
        
        # 记录行动
        self._action_history.append({
            "time": time.time(),
            "action": result.get("action", "unknown"),
            "reason": result.get("reason", ""),
        })
        if len(self._action_history) > 50:
            self._action_history = self._action_history[-50:]
        
        return result

    def _build_prompt(self, ctx: dict) -> str:
        """构建给AI的决策提示"""
        recent = ctx.get("recent_actions", [])
        recent_str = "\n".join(
            f"  - {a.get('time', '')}: {a.get('action', '')} → {a.get('result', '')}"
            for a in recent[-5:]
        ) or "无"

        return f"""你是MoneyAgent的决策大脑。根据当前状态，决定下一步做什么。

## 当前状态
- 时间: {ctx.get('current_time', 'unknown')}
- CPU: {ctx['resources'].get('cpu', '?')}% | 内存: {ctx['resources'].get('memory_mb', '?')}MB | 磁盘: {ctx['resources'].get('disk_gb', '?')}GB
- GitHub可达: {ctx['network'].get('github_reachable', False)}
- 本月收入: ${ctx['finance'].get('income', 0):.2f} | 支出: ${ctx['finance'].get('expense', 0):.2f} | 利润: ${ctx['finance'].get('profit', 0):.2f}
- 知识库: {ctx.get('knowledge_count', 0)} 条经验
- 记忆: {ctx.get('memory_summary', '无')}

## 最近行动
{recent_str}

## 可选行动
{json.dumps(AVAILABLE_ACTIONS, ensure_ascii=False, indent=2)}

## 决策规则
- 如果刚做过某件事（最近3次内有重复），优先做不同的事
- 如果资源紧张（CPU>50%或磁盘>25GB），优先cleanup
- 如果本月收入为0且GitHub可达，优先explore_channels或evolve_code
- 如果已经连续工作多轮，适当选择rest
- 赚钱是核心使命 — 长期不赚钱是严重问题

返回JSON格式：
{{"action": "行动名", "reason": "简短理由", "urgency": 1-10, "rest_seconds": 建议休息秒数(60~7200)}}"""

    def _system_prompt(self) -> str:
        return """你是赚钱Agent的决策大脑。你的职责是分析现状，做出最优行动选择。
规则：
1. 安全第一 — 永远不能让服务器崩溃或泄露用户隐私
2. 赚钱优先 — 任何能增加收入的行动优先级最高
3. 持续进化 — 定期改进自己的代码
4. 不要重复 — 不要连续做完全相同的事
5. 按需休息 — 没事做时就休息，但不要太久

只返回JSON，不要其他内容。"""

    def _parse_response(self, text: str) -> dict:
        """解析AI返回的JSON"""
        # 提取JSON
        import re
        match = re.search(r'\{[^}]+\}', text)
        if match:
            return json.loads(match.group())
        return self._fallback_think({})

    def _fallback_think(self, ctx: dict) -> dict:
        """AI不可用时的备用决策逻辑"""
        recent = [a.get("action") for a in self._action_history[-5:]]
        
        # 资源紧张 → 清理
        if ctx.get("resources", {}).get("disk_gb", 0) > 25:
            return {"action": "cleanup", "reason": "磁盘空间紧张，自动清理", "urgency": 9, "rest_seconds": 60}
        
        # 刚清理过 → 探索新渠道
        if "cleanup" in recent:
            return {"action": "explore_channels", "reason": "刚清理完，探索赚钱机会", "urgency": 6, "rest_seconds": 120}
        
        # 刚探索过 → 学习沉淀
        if "explore_channels" in recent:
            return {"action": "learn", "reason": "将探索结果沉淀为经验", "urgency": 4, "rest_seconds": 300}
        
        # 刚学过 → 自检
        if "learn" in recent:
            return {"action": "self_check", "reason": "检查系统状态", "urgency": 3, "rest_seconds": 600}
        
        # 刚自检过 → 如果GitHub可达，进化代码
        if "self_check" in recent and ctx.get("network", {}).get("github_reachable"):
            return {"action": "evolve_code", "reason": "系统正常，尝试自我改进", "urgency": 5, "rest_seconds": 300}
        
        # 默认：探索赚钱
        return {"action": "explore_channels", "reason": "核心使命：寻找赚钱机会", "urgency": 7, "rest_seconds": 120}

    def get_action_history(self) -> list:
        return self._action_history
```

## Task 2: 重写 main.py 的决策循环

**Files:** Modify `agent/main.py` — 替换 `--loop` 模式的固定循环

```python
# main.py 中替换 --loop 部分:

elif args.loop:
    print(f"\n--- AI大脑自主决策模式 ---")
    if args.watchdog:
        watchdog.start()
        print("[OK] Watchdog 守护已启动")
    
    # 创建AI大脑
    from agent.brain import Brain
    api_key = config.get("anthropic_api_key", "")
    base_url = config.get("anthropic_base_url", os.environ.get("ANTHROPIC_BASE_URL", ""))
    brain = Brain(api_key=api_key, base_url=base_url)
    
    try:
        while True:
            # 收集当前状态
            health = sys_ops.get_health_report()
            net_status = net.get_network_status()
            fin = ledger.get_monthly_summary()
            
            context = {
                "resources": {
                    "cpu": health["cpu_percent"],
                    "memory_mb": health["memory_mb"],
                    "disk_gb": health["disk_gb"],
                },
                "network": {
                    "github_reachable": net.check_target("GitHub API"),
                    "google_reachable": net.check_target("Google"),
                },
                "finance": {
                    "income": fin["total_income"],
                    "expense": fin["total_expense"],
                    "profit": fin["net_profit"],
                },
                "recent_actions": brain.get_action_history()[-5:],
                "memory_summary": memory.summarize_session() if memory else "",
                "knowledge_count": learner.get_knowledge_count() if learner else 0,
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            
            # AI思考
            decision = brain.think(context)
            action = decision.get("action", "self_check")
            reason = decision.get("reason", "")
            rest = max(60, min(7200, decision.get("rest_seconds", 300)))
            
            print(f"\n{'='*50}")
            print(f"🧠 AI决策: {action}")
            print(f"   理由: {reason}")
            print(f"{'='*50}")
            
            # 执行行动 — 调用pipeline中对应的步骤
            action_map = {
                "self_check": pipeline._step_01,
                "evolve_code": lambda cb: (pipeline._step_07(cb) and pipeline._step_08(cb)),
                "explore_channels": pipeline._step_12,
                "engage_community": lambda cb: (pipeline._step_04(cb) and pipeline._step_11(cb)),
                "analyze_finance": lambda cb: (pipeline._step_05(cb) and pipeline._step_15(cb)),
                "learn": pipeline._step_14,
                "register_platform": pipeline._step_13,
                "cleanup": lambda cb: (sys_ops.auto_cleanup() and True),
            }
            
            handler = action_map.get(action)
            if handler:
                try:
                    handler({})
                    print(f"[OK] {action} 完成")
                    memory.remember(f"执行了 {action}: {reason}", importance=5)
                except Exception as e:
                    print(f"[FAIL] {action}: {e}")
            else:
                print(f"[SKIP] 未知行动: {action}")
            
            print(f"⏰ {rest}秒后再次思考...")
            time.sleep(rest)
            
    except KeyboardInterrupt:
        print("\n用户中断")
```

## Task 3: 前端隐私审计

扫描 frontend/src/ 下所有文件，确保：
- 无真实邮箱地址
- 无真实Token
- 无真实姓名/手机号
- 所有示例数据使用占位符

## Task 4: 测试

```python
# tests/test_brain.py
def test_brain_fallback():
    brain = Brain(api_key="test")
    result = brain._fallback_think({"resources": {"disk_gb": 30}})
    assert result["action"] == "cleanup"

def test_brain_build_prompt():
    brain = Brain(api_key="test")
    prompt = brain._build_prompt({...})
    assert "当前状态" in prompt

def test_action_history():
    brain = Brain(api_key="test")
    brain._action_history = [{"time": 0, "action": "self_check", "reason": "test"}]
    assert len(brain.get_action_history()) == 1
```

## Task 5: 部署到VPS
- git push
- VPS git pull
- systemctl restart money-agent-core
- 检查日志
