"""隐私过滤器 — 出站内容自动脱敏"""


class PrivacyFilter:
    """在内容发出前过滤敏感个人信息"""

    def __init__(self, **personal_data):
        """
        personal_data 可包含:
        - user_real_name: 用户真实姓名
        - user_phone: 用户手机号
        - user_address: 用户地址
        - user_id_card: 用户身份证号
        - user_bank_card: 用户银行卡号
        """
        self._sensitive_items = []
        for key, value in personal_data.items():
            if value:
                label = key.replace("user_", "").replace("_", " ")
                self._sensitive_items.append((value, f"[{label}已脱敏]"))

    def filter(self, text: str) -> str:
        """过滤文本中的敏感信息"""
        result = text
        for sensitive, replacement in self._sensitive_items:
            result = result.replace(sensitive, replacement)
        return result

    def add_sensitive(self, value: str, label: str):
        """动态添加敏感信息"""
        self._sensitive_items.append((value, f"[{label}已脱敏]"))

    def filter_dict(self, data: dict) -> dict:
        """递归过滤字典中的所有字符串值"""
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                result[k] = self.filter(v)
            elif isinstance(v, dict):
                result[k] = self.filter_dict(v)
            elif isinstance(v, list):
                result[k] = [
                    self.filter(item) if isinstance(item, str) else item
                    for item in v
                ]
            else:
                result[k] = v
        return result
