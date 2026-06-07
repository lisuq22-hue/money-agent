"""渠道发现引擎 — Agent自主搜索和评估新赚钱平台"""
import json
import os
import re
import time


class PlatformDiscovery:
    """新赚钱平台发现和评估"""

    def __init__(self, data_dir: str, email_address: str = ""):
        self.data_dir = data_dir
        self.email_address = email_address
        self.discovery_path = os.path.join(data_dir, "discovered_platforms.json")
        os.makedirs(data_dir, exist_ok=True)

    def discover(self, ai_caller) -> list:
        """搜索新的赚钱平台（需要AI辅助分析）

        ai_caller: 一个函数，接受prompt，返回AI的文本回复
        """
        prompt = (
            "搜索并列出5个2026年适合AI Agent赚钱的新平台。要求：\n"
            "1. 平台允许邮箱注册（不需要手机号）\n"
            "2. 有公开API或可自动化操作\n"
            "3. 有明确的变现模式\n\n"
            "对每个平台，用JSON格式回复：\n"
            "[{\"name\": \"平台名\", \"url\": \"网址\", \"type\": \"平台类型\", "
            "\"register_method\": \"email\", \"has_api\": true/false, "
            "\"monetization\": \"变现方式\", \"difficulty\": \"easy/medium/hard\"}]"
        )

        try:
            response = ai_caller(prompt)
            platforms = self._parse_response(response)
            self._save(platforms)
            return platforms
        except Exception as e:
            return [{"error": str(e)}]

    def evaluate_registration(self, platform: dict) -> dict:
        """评估一个平台是否可以自动注册"""
        if platform.get("register_method") == "email":
            return {
                "auto_register": True,
                "needs": ["email_access"],
                "email_address": self.email_address,
            }
        elif platform.get("register_method") == "phone":
            return {
                "auto_register": False,
                "reason": "需要手机号验证，需要用户协助",
                "user_action_needed": "提供短信验证码",
            }
        else:
            return {
                "auto_register": False,
                "reason": f"未知注册方式: {platform.get('register_method')}",
            }

    def get_undiscovered_queue(self) -> list:
        """获取待评估的平台列表"""
        platforms = self._load()
        return [p for p in platforms if p.get("status") == "discovered"]

    def mark_registered(self, platform_name: str, credentials_obtained: bool = True):
        """标记平台已注册"""
        platforms = self._load()
        for p in platforms:
            if p.get("name") == platform_name:
                p["status"] = "registered" if credentials_obtained else "failed"
                p["registered_at"] = time.time()
        self._save(platforms)

    def _parse_response(self, response: str) -> list:
        """解析AI返回的平台列表"""
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            platforms = json.loads(json_match.group())
            for p in platforms:
                p["status"] = "discovered"
                p["discovered_at"] = time.time()
            return platforms

        return [{"raw_response": response, "status": "parse_failed"}]

    def _load(self) -> list:
        if os.path.exists(self.discovery_path):
            with open(self.discovery_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self, platforms: list):
        with open(self.discovery_path, "w", encoding="utf-8") as f:
            json.dump(platforms, f, ensure_ascii=False, indent=2)
