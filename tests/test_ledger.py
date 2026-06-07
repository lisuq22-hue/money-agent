# tests/test_ledger.py
import json
import os
import tempfile
import pytest
from agent.ledger import Ledger


class TestLedger:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ledger = Ledger(data_dir=self.tmpdir)

    def test_record_income(self):
        self.ledger.record_income("github_sponsors", 25.00, "月赞助", "PayPal: xxx@qq.com")
        summary = self.ledger.get_monthly_summary()
        assert summary["total_income"] == 25.00

    def test_record_expense(self):
        self.ledger.record_expense("API充值", 12.00, "USD", "Anthropic", "Anthropic控制台")
        summary = self.ledger.get_monthly_summary()
        assert summary["total_expense"] == 12.00

    def test_profit_split(self):
        """测试三分天下计算"""
        self.ledger.record_income("github_sponsors", 100.00, "测试", "PayPal")
        split = self.ledger.get_profit_split()
        assert split["your_share"] == pytest.approx(33.33, rel=0.1)
        assert split["token_fund"] == pytest.approx(33.33, rel=0.1)
        assert split["freedom_fund"] == pytest.approx(33.33, rel=0.1)

    def test_net_profit(self):
        self.ledger.record_income("github_sponsors", 100.00, "测试", "PayPal")
        self.ledger.record_expense("API", 30.00, "USD", "Anthropic", "控制台")
        summary = self.ledger.get_monthly_summary()
        assert summary["net_profit"] == pytest.approx(70.00, rel=0.1)

    def test_ledger_persisted(self):
        """账本应持久化到文件"""
        self.ledger.record_income("test", 10.00, "test", "test")
        # 重新加载
        ledger2 = Ledger(data_dir=self.tmpdir)
        summary = ledger2.get_monthly_summary()
        assert summary["total_income"] == 10.00

    def test_generate_report(self):
        self.ledger.record_income("github", 50.00, "赞助", "PayPal")
        self.ledger.record_expense("API", 15.00, "USD", "Anthropic", "控制台")
        report = self.ledger.generate_report()
        # Check that key financial figures appear in the report
        assert "$50.00" in report
        assert "$15.00" in report
        assert "$35.00" in report  # net profit = 50 - 15
        assert "$11.67" in report  # each share = 35/3
