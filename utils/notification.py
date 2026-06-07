"""通知模块 — 向用户发送消息"""
import json
import os
import time


class NotificationService:
    """通知服务 — MVP阶段用文件+控制台，后续可扩展微信/邮件"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.notify_path = os.path.join(data_dir, "notifications.json")
        os.makedirs(data_dir, exist_ok=True)

    def send(self, title: str, body: str, level: str = "info", action_needed: bool = False):
        """发送通知"""
        notification = {
            "time": time.time(),
            "title": title,
            "body": body,
            "level": level,
            "action_needed": action_needed,
            "read": False,
        }

        # 存到文件
        notifications = self._load()
        notifications.append(notification)
        self._save(notifications)

        # 打印到控制台
        emoji = {"info": "[i]", "warning": "[!]", "error": "[X]", "success": "[OK]"}.get(level, "")
        print(f"\n{emoji} [{level.upper()}] {title}")
        print(f"   {body}")
        if action_needed:
            print(f"   >>> 需要你的操作！")

    def send_alert(self, title: str, body: str):
        """发送告警（需要用户关注）"""
        self.send(title, body, level="warning", action_needed=True)

    def send_error(self, title: str, body: str):
        """发送错误"""
        self.send(title, body, level="error", action_needed=True)

    def send_payment_request(self, amount: float, reason: str, payee: str) -> dict:
        """发送支付请求"""
        request = {
            "id": str(int(time.time())),
            "amount": amount,
            "reason": reason,
            "payee": payee,
            "status": "pending",
            "created_at": time.time(),
        }
        payment_path = os.path.join(self.data_dir, "payment_requests.json")
        requests = []
        if os.path.exists(payment_path):
            with open(payment_path, "r") as f:
                requests = json.load(f)
        requests.append(request)
        with open(payment_path, "w") as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)

        self.send(
            "支付请求",
            f"金额: ${amount}\n用途: {reason}\n收款方: {payee}\n"
            f"请审批: 编辑 data/payment_requests.json 将status改为approved或rejected",
            level="warning",
            action_needed=True,
        )
        return request

    def get_unread(self) -> list:
        """获取未读通知"""
        return [n for n in self._load() if not n["read"]]

    def mark_all_read(self):
        """全部标为已读"""
        notifications = self._load()
        for n in notifications:
            n["read"] = True
        self._save(notifications)

    def _load(self) -> list:
        if os.path.exists(self.notify_path):
            with open(self.notify_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self, notifications: list):
        with open(self.notify_path, "w", encoding="utf-8") as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
