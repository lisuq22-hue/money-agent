# tests/test_config.py
import os
import tempfile
import pytest
from utils.config import load_config


def test_load_config_from_env_and_file():
    """配置应从 .env 文件和系统环境变量加载"""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = os.path.join(tmpdir, ".env")
        with open(env_path, "w") as f:
            f.write("GITHUB_TOKEN=ghp_test123\n")
            f.write("ANTHROPIC_API_KEY=sk-ant-test456\n")

        config = load_config(env_path)

        assert config["github_token"] == "ghp_test123"
        assert config["anthropic_api_key"] == "sk-ant-test456"


def test_load_config_nonexistent_file():
    """配置文件不存在不应崩溃，返回空字典"""
    config = load_config("/nonexistent/path/.env")
    assert isinstance(config, dict)


def test_load_config_missing_optional_keys():
    """可选配置缺失时应有默认值"""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = os.path.join(tmpdir, ".env")
        with open(env_path, "w") as f:
            f.write("GITHUB_TOKEN=ghp_test\n")

        config = load_config(env_path)

        assert config["github_token"] == "ghp_test"
        assert "qq_email_address" in config
        assert config["qq_email_address"] == ""
