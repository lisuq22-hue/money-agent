"""经验学习系统 — Agent总结赚钱和进化经验，沉淀知识库"""
import json
import os
import time
from datetime import datetime
from typing import Optional


class Learner:
    """从赚钱和进化历史中提取经验教训"""

    def __init__(self, project_dir: str, data_dir: str):
        self.project_dir = project_dir
        self.data_dir = data_dir
        self.knowledge_dir = os.path.join(data_dir, 'knowledge')
        os.makedirs(self.knowledge_dir, exist_ok=True)

        # 经验文件
        self.money_wisdom_path = os.path.join(self.knowledge_dir, 'money_wisdom.json')
        self.evolution_wisdom_path = os.path.join(self.knowledge_dir, 'evolution_wisdom.json')
        self.strategy_path = os.path.join(self.knowledge_dir, 'strategy.json')

    # === 赚钱经验 ===

    def learn_from_ledger(self, ledger_data: dict) -> dict:
        """从账本数据中提取赚钱经验"""
        months = ledger_data.get('months', {})
        if not months:
            return {'learned': False, 'reason': '暂无账本数据'}

        insights = {
            'total_months': len(months),
            'best_month': None,
            'best_income': 0,
            'income_trend': 'unknown',
            'suggestions': [],
        }

        # 找最好的月份
        income_history = []
        for month, data in sorted(months.items()):
            income = sum(i.get('amount', 0) for i in data.get('income', []))
            expense = sum(e.get('amount', 0) for e in data.get('expenses', []))
            income_history.append({'month': month, 'income': income, 'expense': expense, 'profit': income - expense})

            if income > insights['best_income']:
                insights['best_income'] = income
                insights['best_month'] = month

        # 判断趋势
        if len(income_history) >= 2:
            recent = income_history[-2:]
            if recent[1]['income'] > recent[0]['income']:
                insights['income_trend'] = 'rising'
                insights['suggestions'].append('收入在增长，保持当前策略')
            elif recent[1]['income'] < recent[0]['income']:
                insights['income_trend'] = 'falling'
                insights['suggestions'].append('收入下降，需要探索新渠道')
            else:
                insights['income_trend'] = 'stable'

        # ROI分析
        total_income = sum(h['income'] for h in income_history)
        total_expense = sum(h['expense'] for h in income_history)
        if total_expense > 0:
            roi = total_income / total_expense
            if roi > 3:
                insights['suggestions'].append(f'ROI={roi:.1f}x — 可以适当加大Token投入')
            elif roi < 1.5:
                insights['suggestions'].append(f'ROI={roi:.1f}x — 需要优化Token使用效率')

        self._save_wisdom(self.money_wisdom_path, insights, income_history)
        return insights

    def learn_from_channels(self, channels_data: list) -> dict:
        """从渠道数据中学习"""
        active = [c for c in channels_data if c.get('enabled')]
        earning = [c for c in active if c.get('revenue', 0) > 0]

        insights = {
            'active_channels': len(active),
            'earning_channels': len(earning),
            'suggestions': [],
        }

        if len(earning) == 0 and len(active) > 0:
            insights['suggestions'].append('已启用的渠道尚未产生收入，需要更多时间或调整策略')

        if len(active) < 3:
            insights['suggestions'].append('活跃渠道少于3个 — 建议搜索和注册新平台')

        return insights

    # === 进化经验 ===

    def learn_from_evolution(self, evolution_logs: list) -> dict:
        """从进化日志中学习"""
        if not evolution_logs:
            return {'learned': False, 'reason': '暂无进化记录'}

        insights = {
            'total_evolutions': len(evolution_logs),
            'recent_activity': 'active' if len(evolution_logs) > 2 else 'sparse',
            'commit_frequency': f'{len(evolution_logs)} 次提交',
            'suggestions': [],
        }

        # 分析提交信息中的模式
        evolve_keywords = ['evolve', 'feat', 'fix', 'refactor']
        keyword_counts = {k: 0 for k in evolve_keywords}
        for log in evolution_logs:
            msg = log.get('message', '').lower()
            for k in evolve_keywords:
                if k in msg:
                    keyword_counts[k] += 1

        if keyword_counts.get('fix', 0) > keyword_counts.get('feat', 0):
            insights['suggestions'].append('修复多于新功能 — 代码质量可能需要关注')

        if len(evolution_logs) < 5:
            insights['suggestions'].append('进化次数较少 — 考虑缩短进化间隔')

        self._save_wisdom(self.evolution_wisdom_path, insights, evolution_logs)
        return insights

    # === 综合策略 ===

    def synthesize_strategy(self, money_insights: dict, evo_insights: dict,
                            resource_status: dict) -> dict:
        """综合所有信息，生成行动策略"""
        strategy = {
            'timestamp': datetime.now().isoformat(),
            'priorities': [],
            'warnings': [],
            'next_actions': [],
        }

        # 收入优先
        if money_insights.get('income_trend') == 'falling':
            strategy['priorities'].append('探索新赚钱渠道（收入下降中）')
            strategy['next_actions'].append('运行渠道发现引擎')
        elif money_insights.get('income_trend') == 'rising':
            strategy['priorities'].append('加大现有渠道投入（收入增长中）')

        # 资源检查
        if not resource_status.get('healthy', True):
            strategy['warnings'].append('服务器资源紧张')
            strategy['next_actions'].append('执行自动清理')

        # 进化检查
        if len(evo_insights.get('suggestions', [])) > 0:
            strategy['next_actions'].extend(evo_insights['suggestions'])

        # 渠道扩充
        active = money_insights.get('active_channels', 0)
        if active < 3:
            strategy['priorities'].append(f'渠道过少 ({active}个)，寻找新平台')

        self._save(strategy, self.strategy_path)
        return strategy

    # === 知识沉淀 ===

    def save_to_knowledge_base(self, topic: str, content: str, tags: list = None):
        """将一条知识写入知识库"""
        filename = f"{int(time.time())}_{topic.replace(' ', '_')[:50]}.md"
        filepath = os.path.join(self.knowledge_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {topic}\n\n")
            f.write(f"时间: {datetime.now().isoformat()}\n")
            if tags:
                f.write(f"标签: {', '.join(tags)}\n")
            f.write(f"\n{content}\n")

    def get_all_knowledge(self, topic_filter: str = None) -> list:
        """获取知识库中的所有条目"""
        entries = []
        for f in sorted(os.listdir(self.knowledge_dir), reverse=True):
            if f.endswith('.md'):
                path = os.path.join(self.knowledge_dir, f)
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                if topic_filter is None or topic_filter.lower() in content.lower():
                    entries.append({
                        'file': f,
                        'content': content[:500],
                    })
        return entries[:50]

    def get_knowledge_count(self) -> int:
        return len([f for f in os.listdir(self.knowledge_dir) if f.endswith('.md')])

    def generate_weekly_report(self, ledger_data: dict, evo_logs: list) -> str:
        """生成周报"""
        money = self.learn_from_ledger(ledger_data)
        evo = self.learn_from_evolution(evo_logs)

        lines = [
            f"# 赚钱Agent 周报",
            f"日期: {datetime.now().strftime('%Y-%m-%d')}",
            f"",
            f"## 财务摘要",
            f"- 累计月份: {money.get('total_months', 0)}",
            f"- 最佳月份: {money.get('best_month', 'N/A')} (${money.get('best_income', 0):.2f})",
            f"- 收入趋势: {money.get('income_trend', 'unknown')}",
            f"",
            f"## 进化摘要",
            f"- 进化次数: {evo.get('total_evolutions', 0)}",
            f"- 活跃度: {evo.get('recent_activity', 'unknown')}",
            f"",
            f"## 知识库",
            f"- 沉淀知识条数: {self.get_knowledge_count()}",
            f"",
            f"## 建议",
        ]

        for s in money.get('suggestions', []) + evo.get('suggestions', []):
            lines.append(f"- {s}")

        report = '\n'.join(lines)
        report_path = os.path.join(self.knowledge_dir, f'weekly_report_{datetime.now().strftime("%Y%m%d")}.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return report

    # === 内部方法 ===

    def _save_wisdom(self, path: str, insights: dict, data: list):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'insights': insights,
                'data_summary': data[-10:] if isinstance(data, list) else data,
                'updated_at': datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)

    def _save(self, data: dict, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
