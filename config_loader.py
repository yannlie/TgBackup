"""统一配置加载器，支持 YAML 和 JSON"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Optional, Union

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器，自动识别 YAML 和 JSON"""

    def __init__(self, config_path: Union[str, Path]):
        """
        Args:
            config_path: 配置文件路径，支持 .yaml/.yml/.json
        """
        self.config_path = Path(config_path)
        self.data = {}
        self._load()

    def _load(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        suffix = self.config_path.suffix.lower()

        try:
            if suffix in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError("需要安装 PyYAML: pip install PyYAML")
                self.data = self._load_yaml()
            elif suffix == '.json':
                self.data = self._load_json()
            else:
                raise ValueError(f"不支持的配置文件格式: {suffix}")

            logger.info(f"✓ 配置文件已加载: {self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise

    def _load_yaml(self) -> dict:
        """加载 YAML 配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _load_json(self) -> dict:
        """加载 JSON 配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """支持字典访问"""
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        """支持 in 操作"""
        return key in self.data


def find_config_file(base_name: str = "telegram_config") -> Optional[Path]:
    """
    自动查找配置文件（优先级：YAML > JSON）

    Args:
        base_name: 配置文件基础名（不含扩展名）

    Returns:
        找到的配置文件路径，或 None
    """
    possible_paths = [
        f"config/{base_name}.yaml",
        f"config/{base_name}.yml",
        f"config/{base_name}.json",
        f"{base_name}.yaml",
        f"{base_name}.yml",
        f"{base_name}.json",
    ]

    for path_str in possible_paths:
        path = Path(path_str)
        if path.exists():
            logger.info(f"找到配置文件: {path}")
            return path

    return None


# 向后兼容的类
class TelegramConfig(ConfigLoader):
    """Telegram 配置类（兼容旧代码）"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 配置文件路径，为 None 则自动查找
        """
        if config_path is None:
            # 自动查找配置文件
            found_path = find_config_file("telegram_config")
            if found_path is None:
                raise FileNotFoundError(
                    "找不到配置文件！请创建以下任一文件：\n"
                    "  - config/telegram_config.yaml (推荐)\n"
                    "  - config/telegram_config.json\n"
                    "  - telegram_config.yaml\n"
                    "  - telegram_config.json"
                )
            config_path = str(found_path)

        super().__init__(config_path)


class Config(ConfigLoader):
    """通用配置类（兼容旧代码）"""
    pass


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)

    try:
        config = TelegramConfig()
        print(f"API ID: {config.get('api_id')}")
        print(f"Channels: {config.get('channels', [])}")
    except Exception as e:
        print(f"测试失败: {e}")
