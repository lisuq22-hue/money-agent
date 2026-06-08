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
        print(f"\n--- 24/7持续运行模式 (每{args.interval}秒一轮) ---")
        if args.watchdog:
            watchdog.start()
            print("[OK] Watchdog 守护已启动")

        try:
            while True:
                run_one_cycle()
                print(f"\n{ledger.generate_report()}")
                print(f"下一轮: {args.interval}秒后...")
                time.sleep(args.interval)
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
