# tests/test_privacy_filter.py
import pytest
from core.privacy_filter import PrivacyFilter


class TestPrivacyFilter:
    def setup_method(self):
        self.pf = PrivacyFilter(
            user_real_name="张三",
            user_phone="13800138000",
            user_address="北京市朝阳区xxx路123号",
            user_id_card="110101199001011234",
            user_bank_card="6222021234567890123",
        )

    def test_filter_real_name(self):
        result = self.pf.filter("我的名字是张三")
        assert "张三" not in result

    def test_filter_phone_number(self):
        result = self.pf.filter("联系电话：13800138000")
        assert "13800138000" not in result

    def test_filter_address(self):
        result = self.pf.filter("地址是北京市朝阳区xxx路123号")
        assert "北京市朝阳区xxx路123号" not in result

    def test_filter_id_card(self):
        result = self.pf.filter("身份证110101199001011234")
        assert "110101199001011234" not in result

    def test_filter_bank_card(self):
        result = self.pf.filter("卡号6222021234567890123")
        assert "6222021234567890123" not in result

    def test_safe_content_passes_through(self):
        """安全内容应原样通过"""
        safe_text = "今天天气很好，适合写代码。Python是一门优秀的语言。"
        result = self.pf.filter(safe_text)
        assert result == safe_text

    def test_replacement_marker(self):
        """敏感内容被替换后应有标记"""
        result = self.pf.filter("我是张三")
        assert "张三" not in result
        assert "脱敏" in result


class TestPrivacyFilterNoPersonalData:
    def setup_method(self):
        self.pf = PrivacyFilter()  # 不设个人信息

    def test_no_data_still_works(self):
        result = self.pf.filter("普通文本")
        assert result == "普通文本"
