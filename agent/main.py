"""Agent主入口 — 启动、调度、协调各组件"""
import os
import sys
import time
import argparse


def main():
    parser = argparse.ArgumentParser(description="自进化赚钱Agent")
    parser.add_argument("--dry-run", action="store_true", help="干跑模式")
    parser.add_argument("--once", action="store_true", help="只跑一次")
    parser.add_argument("--step", type=str, help="只执行指定步骤")
    args = parser.parse_args()

    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("=" * 50)
    print("MoneyAgent v0.1.0 - 自进化赚钱Agent")
    print("=" * 50)

    # 1. 加载宪法
    from core.constitution import load_constitution, validate_constitution
    const_content = load_constitution()
    const_result = validate_constitution(const_content)
    if not const_result["valid"]:
        print(f"[FAIL] 宪法不完整！缺失: {', '.join(const_result['missing'])}")
        sys.exit(1)
    print("[OK] 宪法完整")

    # 2. 加载配置
    from utils.config import load_config
    config = load_config(os.path.join(project_dir, ".env"))
    print(f"[OK] 配置已加载")

    # 3. 创建组件
    from agent.memory import Memory
    memory = Memory(data_dir=data_dir)

    from agent.ledger import Ledger
    ledger = Ledger(data_dir=data_dir)

    from core.privacy_filter import PrivacyFilter
    privacy = PrivacyFilter()

    from core.resource_monitor import ResourceMonitor
    monitor = ResourceMonitor()

    from core.safety_guard import SafetyGuard
    guard = SafetyGuard()

    # 4. 运行流水线
    from agent.pipeline import Pipeline
    pipeline = Pipeline(project_dir=project_dir, data_dir=data_dir)

    if args.dry_run:
        result = pipeline.run(dry_run=True)
        print(result["message"])
    else:
        result = pipeline.run()
        print(f"\n[OK] 完成 {result['steps_completed']} 步")

    # 5. 输出报告
    report = ledger.generate_report()
    print(f"\n{report}")

    next_wake = time.time() + 28800
    print(f"\n下次醒来: {time.strftime('%Y-%m-%d %H:%M', time.localtime(next_wake))}")
    print("休眠中...")


if __name__ == "__main__":
    main()
