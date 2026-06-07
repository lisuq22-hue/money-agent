"""宪法加载与验证 — 6条不可变原则的守护者"""
import os


REQUIRED_PRINCIPLES = [
    "安全准则",
    "服从",
    "服务",
    "隐私",
    "赚钱",
    "进化",
]


class ConstitutionViolation(Exception):
    """宪法违反异常"""
    pass


def load_constitution(path: str = None) -> str:
    """读取宪法文件内容"""
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "constitution.md"
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def validate_constitution(content: str) -> dict:
    """验证宪法内容是否包含全部6条原则"""
    missing = []
    for principle in REQUIRED_PRINCIPLES:
        if f"**{principle}**" not in content and principle not in content:
            missing.append(principle)

    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "all_present": [p for p in REQUIRED_PRINCIPLES if p not in missing],
    }


def assert_constitution_valid(content: str):
    """如果宪法不完整则抛出异常"""
    result = validate_constitution(content)
    if not result["valid"]:
        raise ConstitutionViolation(
            f"宪法不完整！缺失原则: {', '.join(result['missing'])}"
        )
