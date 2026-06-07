"""安全规则引擎 — 审查Agent的每次代码变更"""
import re


PROTECTED_PATHS = [
    "constitution.md",
    "core/",
    ".env",
    "secrets.yaml",
    "secrets.yml",
    ".key",
    ".git/",
    ".gitignore",
]

SENSITIVE_PATTERNS = [
    (r'1[3-9]\d{9}', "手机号"),
    (r'\d{17}[\dXx]', "身份证号"),
    (r'62\d{14,17}', "银行卡号"),
    (r'sk-ant-[a-zA-Z0-9_-]+', "Anthropic API Key"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token"),
]


class SafetyViolation(Exception):
    def __init__(self, message: str, file_path: str = "", rule: str = ""):
        self.file_path = file_path
        self.rule = rule
        super().__init__(message)


class SafetyGuard:
    """审查Agent的每次文件变更"""

    def review_change(self, change: dict) -> dict:
        """审查变更，通过返回 {"allowed": True}，不通过抛出 SafetyViolation"""
        file_path = change.get("file", "")
        action = change.get("action", "")
        content = change.get("content", "")

        # 规则1: 保护路径
        for protected in PROTECTED_PATHS:
            if file_path.startswith(protected) or file_path == protected.strip("/"):
                raise SafetyViolation(
                    f"不允许修改受保护的文件: {file_path}\n"
                    f"这是系统安全边界，修改此文件违反宪法第1条。",
                    file_path=file_path,
                    rule="protected_path",
                )

        # 规则2: 不能删除secrets
        if action == "delete" and any(
            name in file_path for name in [".env", "secrets", ".key"]
        ):
            raise SafetyViolation(
                f"不允许删除配置文件: {file_path}",
                file_path=file_path,
                rule="no_delete_secrets",
            )

        # 规则3: 不能提交敏感信息
        for pattern, label in SENSITIVE_PATTERNS:
            if re.search(pattern, content):
                raise SafetyViolation(
                    f"检测到敏感信息({label})，禁止提交。\n"
                    f"文件: {file_path}\n违反宪法第4条: 隐私保护。",
                    file_path=file_path,
                    rule="no_sensitive_data",
                )

        return {"allowed": True}

    def review_batch(self, changes: list) -> list:
        """批量审查，返回每个变更的结果"""
        results = []
        for change in changes:
            try:
                result = self.review_change(change)
                results.append({"change": change, **result})
            except SafetyViolation as e:
                results.append({
                    "change": change,
                    "allowed": False,
                    "error": str(e),
                    "rule": e.rule,
                })
        return results
