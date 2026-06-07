"""QQ邮箱工具 — IMAP收验证码"""
import imaplib
import email
import re
import time
from email.header import decode_header


class EmailReader:
    """QQ邮箱IMAP读取器 — 用于自动接收验证码邮件"""

    def __init__(self, address: str, auth_code: str, imap_server: str = "imap.qq.com"):
        self.address = address
        self.auth_code = auth_code
        self.imap_server = imap_server
        self._conn = None

    def connect(self) -> bool:
        """连接邮箱"""
        try:
            self._conn = imaplib.IMAP4_SSL(self.imap_server, 993)
            self._conn.login(self.address, self.auth_code)
            return True
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"邮箱登录失败: {e}（请检查QQ邮箱授权码是否正确）")

    def disconnect(self):
        """断开连接"""
        if self._conn:
            try:
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    def wait_for_code(self, sender_contains: str = "", timeout: int = 120,
                      code_length: int = 6) -> str | None:
        """等待验证码邮件并提取验证码"""
        if not self._conn:
            self.connect()

        start = time.time()
        while time.time() - start < timeout:
            try:
                code = self._search_latest_code(sender_contains, code_length)
                if code:
                    return code
            except Exception:
                pass
            time.sleep(5)

        return None

    def _search_latest_code(self, sender_contains: str, code_length: int) -> str | None:
        """搜索最新邮件中的验证码"""
        self._conn.select("INBOX")

        # 搜索未读邮件
        status, messages = self._conn.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            return None

        msg_ids = messages[0].split()
        # 检查最新的几封
        for msg_id in reversed(msg_ids[-5:]):
            status, msg_data = self._conn.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # 检查发件人
                    sender = msg.get("From", "")
                    if sender_contains and sender_contains.lower() not in sender.lower():
                        continue

                    # 解析邮件内容
                    content = self._get_email_body(msg)
                    if not content:
                        continue

                    # 提取验证码
                    code = self._extract_code(content, code_length)
                    if code:
                        return code

        return None

    def _get_email_body(self, msg) -> str:
        """提取邮件正文"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += self._decode_str(payload)
                    except Exception:
                        continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = self._decode_str(payload)
            except Exception:
                pass
        return body

    def _decode_str(self, data: bytes) -> str:
        """解码字节为字符串"""
        for encoding in ["utf-8", "gbk", "gb2312", "latin-1"]:
            try:
                return data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        return data.decode("utf-8", errors="replace")

    def _extract_code(self, text: str, length: int = 6) -> str | None:
        """从文本中提取验证码"""
        # 常见的验证码模式
        patterns = [
            rf"验证码[：:]\s*(\d{{{length}}})",
            rf"code[：:]\s*(\d{{{length}}})",
            rf"(\d{{{length}}})\s*是您的验证码",
            rf"verification code[：:]\s*(\d{{{length}}})",
            rf"(\d{{{length}}})",  # 最后的兜底模式
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None


def test_email_connection(address: str, auth_code: str, imap_server: str = "imap.qq.com") -> bool:
    """测试邮箱连接"""
    reader = EmailReader(address, auth_code, imap_server)
    try:
        reader.connect()
        reader.disconnect()
        return True
    except Exception as e:
        print(f"邮箱连接失败: {e}")
        return False
