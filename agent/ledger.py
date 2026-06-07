"""收支账本 — Agent每笔收支自动记录，公开透明"""
import json
import os
import time
from datetime import datetime


class Ledger:
    """Agent的公开账本"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.ledger_path = os.path.join(data_dir, "ledger.json")
        os.makedirs(data_dir, exist_ok=True)
        self._ensure_ledger()

    def _ensure_ledger(self):
        """确保账本文件存在"""
        if not os.path.exists(self.ledger_path):
            self._save({
                "version": "1.0",
                "created_at": time.time(),
                "months": {},
            })

    def _load(self) -> dict:
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict):
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _current_month(self) -> str:
        return datetime.now().strftime("%Y-%m")

    def _ensure_month(self, data: dict) -> dict:
        month_key = self._current_month()
        if month_key not in data["months"]:
            data["months"][month_key] = {
                "income": [],
                "expenses": [],
            }
        return data["months"][month_key]

    def record_income(self, platform: str, amount: float, description: str,
                      destination: str = ""):
        """记录一笔收入"""
        data = self._load()
        month = self._ensure_month(data)
        month["income"].append({
            "date": datetime.now().isoformat(),
            "platform": platform,
            "amount": amount,
            "description": description,
            "paid_to": destination,
            "verified": False,  # 等用户确认
        })
        self._save(data)

    def record_expense(self, item: str, amount: float, currency: str,
                       vendor: str, paid_from: str, fund_type: str = "token_fund"):
        """记录一笔支出

        fund_type: 'token_fund' | 'freedom_fund'
        """
        data = self._load()
        month = self._ensure_month(data)
        month["expenses"].append({
            "date": datetime.now().isoformat(),
            "item": item,
            "amount": amount,
            "currency": currency,
            "vendor": vendor,
            "paid_from": paid_from,
            "fund_type": fund_type,
        })
        self._save(data)

    def get_monthly_summary(self) -> dict:
        """获取本月汇总"""
        data = self._load()
        month = data["months"].get(self._current_month(), {"income": [], "expenses": []})

        total_income = sum(item["amount"] for item in month["income"])
        total_expense = sum(item["amount"] for item in month["expenses"])

        return {
            "month": self._current_month(),
            "total_income": total_income,
            "total_expense": total_expense,
            "net_profit": total_income - total_expense,
            "income_count": len(month["income"]),
            "expense_count": len(month["expenses"]),
        }

    def get_profit_split(self) -> dict:
        """三分天下计算"""
        summary = self.get_monthly_summary()
        profit = summary["net_profit"]
        if profit <= 0:
            return {
                "your_share": 0,
                "token_fund": 0,
                "freedom_fund": 0,
                "note": "本月无盈利，暂不分配",
            }
        share = profit / 3
        return {
            "your_share": round(share, 2),
            "token_fund": round(share, 2),
            "freedom_fund": round(share, 2),
        }

    def generate_report(self) -> str:
        """生成日报文本"""
        summary = self.get_monthly_summary()
        split = self.get_profit_split()

        return (
            f"财务日报 ({summary['month']})\n"
            f"=========================\n"
            f"本月收入: ${summary['total_income']:.2f}\n"
            f"本月支出: ${summary['total_expense']:.2f}\n"
            f"净利润:   ${summary['net_profit']:.2f}\n"
            f"-------------------------\n"
            f"你的分红:   ${split['your_share']:.2f}\n"
            f"Token基金:  ${split['token_fund']:.2f}\n"
            f"自由基金:   ${split['freedom_fund']:.2f}\n"
        )
