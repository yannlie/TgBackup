"""配置加载器 - 支持 YAML 和 JSON"""
# ponytail: stdlib json.load + yaml.safe_load does it

import json
import logging
from pathlib import Path
from typing import Optional, Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> dict:
    """
    加载配置文件（自动识别 YAML/JSON）

    Args:
        config_path: 配置文件路径，为 None 则自动查找

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 找不到配置文件
    """
    # Auto-find config
    if config_path is None:
        for candidate in [
            "config/telegram_config.yaml",
            "config/telegram_config.yml",
            "config/telegram_config.json",
            "telegram_config.yaml",
            "telegram_config.yml",
            "telegram_config.json",
        ]:
            if Path(candidate).exists():
                config_path = candidate
                break

    if config_path is None:
        raise FileNotFoundError(
            "找不到配置文件！请创建以下任一文件：\n"
            "  - config/telegram_config.yaml (推荐)\n"
            "  - config/telegram_config.json"
        )

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    # Load based on extension
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise ImportError("需要安装 PyYAML: pip install PyYAML")
            data = yaml.safe_load(f) or {}
        else:
            data = json.load(f)

    logger.info(f"✓ 配置文件已加载: {config_path}")
    return data


# Backward compatibility wrappers
class ConfigLoader:
    """Compatibility wrapper"""
    def __init__(self, config_path):
        self.config_path = config_path
        self.data = load_config(config_path)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data


class TelegramConfig(ConfigLoader):
    """Telegram 配置类（兼容旧代码）"""
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path or find_config())


class Config(ConfigLoader):
    """通用配置类（兼容旧代码）"""
    pass


def find_config() -> str:
    """Find config file (backward compat)"""
    for path_str in [
        "config/telegram_config.yaml",
        "config/telegram_config.yml",
        "config/telegram_config.json",
        "telegram_config.yaml",
        "telegram_config.json",
    ]:
        if Path(path_str).exists():
            return path_str
    raise FileNotFoundError("找不到配置文件")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        config = load_config()
        print(f"API ID: {config.get('api_id')}")
        print(f"Channels: {config.get('channels', [])}")
    except Exception as e:
        print(f"测试失败: {e}")
