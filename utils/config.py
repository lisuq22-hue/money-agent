"""配置加载模块 — 从 .env 文件和环境变量中读取配置"""
import os


def load_config(env_path: str = ".env") -> dict:
    """加载配置，优先级：环境变量 > .env 文件"""
    config = {}

    # 先读 .env 文件
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip().lower()] = val.strip()

    # 环境变量覆盖
    env_mappings = {
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        "GITHUB_TOKEN": "github_token",
        "QQ_EMAIL_ADDRESS": "qq_email_address",
        "QQ_EMAIL_AUTH_CODE": "qq_email_auth_code",
        "QQ_IMAP_SERVER": "qq_imap_server",
    }

    for env_key, config_key in env_mappings.items():
        if os.environ.get(env_key):
            config[config_key] = os.environ[env_key]

    # 设置默认值
    defaults = {
        "anthropic_api_key": config.get("anthropic_api_key", ""),
        "github_token": config.get("github_token", ""),
        "qq_email_address": config.get("qq_email_address", ""),
        "qq_email_auth_code": config.get("qq_email_auth_code", ""),
        "qq_imap_server": config.get("qq_imap_server", "imap.qq.com"),
    }
    config.update(defaults)

    return config
