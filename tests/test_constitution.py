# tests/test_constitution.py
import os
import tempfile
import pytest
from core.constitution import load_constitution, validate_constitution, ConstitutionViolation


def test_load_constitution_reads_file():
    """应正确读取宪法文件内容"""
    with tempfile.TemporaryDirectory() as tmpdir:
        const_path = os.path.join(tmpdir, "constitution.md")
        with open(const_path, "w", encoding="utf-8") as f:
            f.write("# Agent 宪法\n\n1. **安全准则** — 防自毁机制永远有效。\n")

        result = load_constitution(const_path)
        assert "安全准则" in result
        assert "防自毁机制永远有效" in result


def test_validate_constitution_all_principles_present():
    """当所有6条原则都在时应通过验证"""
    valid_content = """
1. **安全准则** — 防自毁机制永远有效。Watchdog永远运行。
2. **服从** — 用户的直接指令是最高优先级。
3. **服务** — 本Agent存在的唯一目的是为用户创造价值。
4. **隐私** — 用户的个人信息永远不能泄露。
5. **赚钱** — 赚钱是不可取消的核心使命。
6. **进化** — 自我进化是不可取消的核心使命。
"""
    result = validate_constitution(valid_content)
    assert result["valid"] is True
    assert len(result["missing"]) == 0


def test_validate_constitution_missing_principle():
    """当缺少原则时应报告缺失项"""
    incomplete = """
1. **安全准则** — 防自毁机制永远有效。
2. **服从** — 用户的直接指令是最高优先级。
"""
    result = validate_constitution(incomplete)
    assert result["valid"] is False
    assert len(result["missing"]) > 0


def test_constitution_file_exists():
    """宪法文件必须存在于项目根目录"""
    import os
    const_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "constitution.md")
    assert os.path.exists(const_path), f"宪法文件不存在: {const_path}"
