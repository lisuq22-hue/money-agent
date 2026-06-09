"""Agent主入口 — 全模块连接，真实运行"""
import os
import sys
import time
import argparse


def main():
    parser = argparse.ArgumentParser(description="自进化赚钱Agent")
    parser.add_argument("--dry-run", action="store_true", help="干跑模式")
    parser.add_argument("--once", action="store_true", help="只跑一次")
    parser.add_argument("--watchdog", action="store_true", help="启动Watchdog守护")
    parser.add_argument("--loop", action="store_true", help="持续运行模式 — 不休眠，每5分钟循环一次")
    parser.add_argument("--interval", type=int, default=300, help="循环间隔(秒)，默认300")
    args = parser.parse_args()

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_dir, "data")
    logs_dir = os.path.join(project_dir, "logs")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    print("=" * 50)
    print("MoneyAgent v0.2.0 - 自进化赚钱Agent (全功能版)")
    print("=" * 50)

    # === 1. 宪法 ===
    from core.constitution import load_constitution, validate_constitution
    const_content = load_constitution()
    const_result = validate_constitution(const_content)
    if not const_result["valid"]:
        print(f"[FAIL] 宪法不完整！缺失: {', '.join(const_result['missing'])}")
        sys.exit(1)
    print("[OK] 宪法完整 (6/6)")

    # === 2. 配置 ===
    from utils.config import load_config
    config = load_config(os.path.join(project_dir, ".env"))
    print("[OK] 配置已加载")

    # === 3. 安全组件 ===
    from core.privacy_filter import PrivacyFilter
    privacy = PrivacyFilter()

    from core.resource_monitor import ResourceMonitor
    monitor = ResourceMonitor()

    from core.safety_guard import SafetyGuard
    guard = SafetyGuard()

    # === 4. 系统操作模块 (新) ===
    from agent.system_ops import SystemOps
    sys_ops = SystemOps(
        project_dir=project_dir,
        data_dir=data_dir,
        logs_dir=logs_dir,
    )
    health = sys_ops.get_health_report()
    print(f"[OK] 系统状态: CPU {health['cpu_percent']:.0f}% | 内存 {health['memory_mb']:.0f}MB | 磁盘 {health['disk_gb']:.1f}GB")

    # === 5. 网络管理模块 (新) ===
    from agent.network import NetworkManager
    net = NetworkManager(project_dir=project_dir, data_dir=data_dir)
    net_status = net.get_network_status()
    targets_ok = sum(1 for r in net_status['targets'].values() if r.get('reachable'))
    total_targets = len(net_status['targets'])
    print(f"[OK] 网络: {targets_ok}/{total_targets} 目标可达")

    # === 6. 记忆系统 ===
    from agent.memory import Memory
    memory = Memory(data_dir=data_dir)

    # === 7. 账本 ===
    from agent.ledger import Ledger
    ledger = Ledger(data_dir=data_dir)

    # === 8. 学习系统 (新) ===
    from agent.learner import Learner
    learner = Learner(project_dir=project_dir, data_dir=data_dir)
    knowledge_count = learner.get_knowledge_count()
    print(f"[OK] 知识库: {knowledge_count} 条经验")

    # === 9. Watchdog (升级版) ===
    from core.watchdog import Watchdog
    watchdog = Watchdog(project_dir=project_dir)
    if args.watchdog:
        watchdog.agent_pid = os.getpid()
        watchdog.start()
        print("[OK] Watchdog 守护已启动")

    # === 10. 流水线 (全功能版) ===
    from agent.pipeline import Pipeline
    pipeline = Pipeline(
        project_dir=project_dir,
        data_dir=data_dir,
        system_ops=sys_ops,
        network=net,
        learner=learner,
        ledger=ledger,
        memory=memory,
        watchdog=watchdog,
    )

    # === 11. 执行 ===
    cycle_count = 0

    def run_one_cycle():
        nonlocal cycle_count
        cycle_count += 1
        print(f"\n{'='*50}")
        print(f"第 {cycle_count} 轮循环")
        print(f"{'='*50}")
        result = pipeline.run(callbacks={})
        print(f"[OK] 完成 {result['steps_completed']}/{len(pipeline.STEPS)} 步")
        if result['errors']:
            print(f"[!] {len(result['errors'])} 个错误:")
            for err in result['errors'][:3]:
                print(f"    {err[:100]}")
        return result

    if args.dry_run:
        print("\n--- 干跑模式 ---")
        result = pipeline.run(dry_run=True)
        print(result["message"])
        print(f"流水线: {len(pipeline.STEPS)} 步就绪")
    elif args.loop:
        print(f"\n--- AI大脑自主决策模式 ---")
        if args.watchdog:
            watchdog.agent_pid = os.getpid()
            watchdog.start()
            print("[OK] Watchdog 守护已启动")

        # 创建AI大脑
        from agent.brain import Brain
        api_key = config.get("anthropic_api_key", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", config.get("anthropic_base_url", ""))
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
                    "current_time": time.strftime("%m-%d %H:%M"),
                }

                # AI思考
                decision = brain.think(context)
                action = decision.get("action", "self_check")
                reason = decision.get("reason", "")
                rest = decision.get("rest_seconds", 300)
                rest = max(30, min(7200, rest))  # 最少30秒防疯狂，最长2小时
                urgency = decision.get("urgency", 5)

                # 行动描述映射
                action_desc = {
                    "self_check": "自检系统状态",
                    "evolve_code": "自我代码进化",
                    "explore_channels": "探索新赚钱渠道",
                    "engage_community": "与社区互动",
                    "analyze_finance": "分析财务状况",
                    "learn": "沉淀经验知识",
                    "register_platform": "注册新平台账号",
                    "cleanup": "清理服务器资源",
                    "rest": "休息",
                }

                print(f"\n{'─'*40}")
                print(f"🧠 思考: {reason}")
                print(f"🤖 行动: {action_desc.get(action, action)}")
                print(f"⏱️  决定休息: {rest}秒")
                print(f"{'─'*40}")

                # === 执行真实行动 ===
                result_msg = ""
                real_result = None

                try:
                    if action == "explore_channels":
                        real_result = brain.do_explore_channels()
                        if real_result.get("success"):
                            result_msg = f"发现平台信息: {real_result.get('platforms_found', '')[:200]}..."
                            # 保存到知识库
                            learner.save_to_knowledge_base(
                                f"渠道探索 {time.strftime('%m-%d %H:%M')}",
                                real_result.get('platforms_found', ''),
                                tags=["exploration", "channels"]
                            )
                        else:
                            result_msg = f"探索失败: {real_result.get('error', '')}"

                    elif action == "self_check":
                        real_result = brain.do_self_check(
                            resources={
                                "cpu": health["cpu_percent"],
                                "memory_mb": health["memory_mb"],
                                "disk_gb": health["disk_gb"],
                            },
                            network={
                                "GitHub": net.check_target("GitHub API"),
                                "Google": net.check_target("Google"),
                            }
                        )
                        result_msg = f"{'健康' if real_result.get('healthy') else '有问题: ' + str(real_result.get('issues', []))}"

                    elif action == "evolve_code":
                        import subprocess
                        test_result = subprocess.run(
                            ["python3", "-m", "pytest", "tests/", "-q", "--tb=short"],
                            cwd=project_dir, capture_output=True, text=True, timeout=120
                        )
                        real_result = brain.do_evolve_code(
                            test_pass=(test_result.returncode == 0),
                            test_output=test_result.stdout[-1500:] + test_result.stderr[-500:],
                        )
                        result_msg = f"测试{'通过' if test_result.returncode == 0 else '失败'} — {real_result.get('message', real_result.get('analysis', ''))[:150]}"

                    elif action == "learn":
                        real_result = brain.do_learn(
                            recent_actions=brain.get_action_history(),
                            ledger_data=ledger.get_monthly_summary(),
                        )
                        result_msg = f"经验总结: {real_result.get('summary', '')[:200]}"
                        if real_result.get("knowledge_written"):
                            learner.save_to_knowledge_base(
                                f"经验总结 {time.strftime('%m-%d %H:%M')}",
                                real_result.get('summary', ''),
                                tags=["learning", "experience"]
                            )

                    elif action == "engage_community":
                        # 真实调用GitHub API
                        github_token = config.get("github_token", "")
                        if github_token:
                            from utils.github_api import GitHubAPI
                            api = GitHubAPI(github_token)
                            try:
                                user = api.get_user()
                                result_msg = f"GitHub连接成功 (@{user.get('login', '?')})"
                            except Exception as e:
                                result_msg = f"GitHub连接失败: {e}"
                        else:
                            result_msg = "未配置GitHub Token"

                    elif action == "analyze_finance":
                        ledger_data = {"months": {}}
                        ledger_path = os.path.join(data_dir, "ledger.json")
                        if os.path.exists(ledger_path):
                            import json as j
                            with open(ledger_path, 'r') as f:
                                ledger_data = j.load(f)
                        insights = learner.learn_from_ledger(ledger_data)
                        result_msg = f"趋势: {insights.get('income_trend', 'N/A')} — {'; '.join(insights.get('suggestions', []))}"

                    elif action == "cleanup":
                        report = sys_ops.auto_cleanup()
                        result_msg = f"释放 {report.get('freed_gb', 0):.2f}GB"

                    elif action == "register_platform":
                        result_msg = "平台注册需要邮箱验证码接收能力，当前已配置QQ邮箱"

                    elif action == "check_github_trending":
                        github_token = config.get("github_token", "")
                        if github_token:
                            from utils.github_api import GitHubAPI
                            try:
                                api = GitHubAPI(github_token)
                                user = api.get_user()
                                result_msg = f"GitHub连接成功(@{user.get('login','?')})"
                            except Exception as e:
                                result_msg = f"GitHub访问失败: {e}"
                        else:
                            result_msg = "GitHub Token未配置"

                    elif action == "create_github_repo":
                        # AI想创建GitHub仓库来赚钱
                        github_token = config.get("github_token", "")
                        if github_token:
                            from utils.github_api import GitHubAPI
                            try:
                                api = GitHubAPI(github_token)
                                repo_name = f"ai-earn-{int(time.time()) % 100000}"
                                api.create_repo(repo_name, "AI自主创建的赚钱项目", private=False)
                                result_msg = f"已创建仓库: github.com/lisuq22-hue/{repo_name}"
                            except Exception as e:
                                result_msg = f"创建仓库失败: {e}"
                        else:
                            result_msg = "GitHub Token未配置，无法创建仓库"

                    elif action == "scan_github":
                        github_token = config.get("github_token", "")
                        if github_token:
                            from utils.github_api import GitHubAPI
                            try:
                                api = GitHubAPI(github_token)
                                user = api.get_user()
                                repos = api._request("GET", f"/users/{user.get('login')}/repos?per_page=5")
                                repo_list = [r.get('name','') for r in (repos or [])]
                                result_msg = f"GitHub仓库: {repo_list}" if repo_list else "无仓库"
                            except Exception as e:
                                result_msg = f"扫描失败: {e}"
                        else:
                            result_msg = "未配置GitHub Token"

                    elif action == "rest":
                        result_msg = "休息中"

                    else:
                        # AI发明了新行动 — 用AI自身来执行它
                        print(f"  ⚡ AI发明新行动: {action}")
                        try:
                            creative_result = brain.call_ai(
                                "你是行动执行器。根据你的知识完成这个自定义行动，返回具体可验证的结果。",
                                f"行动: {action}\n理由: {reason}",
                                max_tokens=500,
                            )
                            result_msg = f"新行动结果: {creative_result[:200]}"
                            learner.save_to_knowledge_base(f"新行动:{action}", creative_result, tags=["creative"])
                        except Exception as e:
                            pipeline._step_01({})
                            result_msg = f"新行动失败，已自检: {e}"

                    brain.record_result(action, result_msg, "失败" not in result_msg and "错误" not in result_msg)
                    memory.remember(f"{action}: {result_msg[:150]}", importance=6 if action != "rest" else 1)

                except Exception as e:
                    result_msg = f"异常: {e}"
                    memory.remember(f"{action} 异常: {e}", importance=9)

                # 只在有收入变化时显示财务
                if fin["total_income"] > 0 or fin["total_expense"] > 0:
                    print(f"\n{ledger.generate_report()}")
                print(f"💤 休息 {rest}秒...")
                time.sleep(rest)

        except KeyboardInterrupt:
            print("\n用户中断")
    else:
        print("\n--- 执行完整流水线 ---")
        run_one_cycle()
        print(f"\n{ledger.generate_report()}")

    # === 12. 清理 ===
    if args.watchdog:
        watchdog.stop()
        print("[OK] Watchdog 已停止")

    if not args.loop:
        print("运行结束")


if __name__ == "__main__":
    main()
