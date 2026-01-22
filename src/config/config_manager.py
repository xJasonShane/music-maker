"""
配置管理模块 - 使用单例模式管理API密钥和账号配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any


class ConfigManager:
    """配置管理器 - 单例模式"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config: Dict[str, Any] = {}
        self._env_path: Optional[Path] = None
        self._initialized = True

    def load_config(self, env_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载.env配置文件

        Args:
            env_path: .env文件路径，默认为项目根目录下的.env

        Returns:
            配置字典
        """
        if env_path:
            self._env_path = Path(env_path)
        else:
            self._env_path = Path(__file__).parent.parent.parent / '.env'

        if not self._env_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self._env_path}")

        load_dotenv(self._env_path)

        self._config = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'api_base': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4')
            },
            'app': {
                'output_dir': os.getenv('OUTPUT_DIR', './output'),
                'history_file': os.getenv('HISTORY_FILE', './history.json')
            }
        }

        return self._config

    def save_config(self, config: Dict[str, Any]) -> None:
        """
        保存配置到.env文件

        Args:
            config: 配置字典
        """
        if not self._env_path:
            self._env_path = Path(__file__).parent.parent.parent / '.env'

        lines = []
        if self._env_path.exists():
            with open(self._env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        env_dict = {}
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                env_dict[key.strip()] = value.strip()

        env_dict.update({
            'OPENAI_API_KEY': config.get('openai', {}).get('api_key', ''),
            'OPENAI_API_BASE': config.get('openai', {}).get('api_base', 'https://api.openai.com/v1'),
            'OPENAI_MODEL': config.get('openai', {}).get('model', 'gpt-4'),
            'OUTPUT_DIR': config.get('app', {}).get('output_dir', './output'),
            'HISTORY_FILE': config.get('app', {}).get('history_file', './history.json')
        })

        with open(self._env_path, 'w', encoding='utf-8') as f:
            for key, value in env_dict.items():
                f.write(f"{key}={value}\n")

        self._config = config

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键（如 'openai.api_key'）
            default: 默认值

        Returns:
            配置值
        """
        if not self._config:
            self.load_config()

        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        if not self._config:
            self.load_config()

        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_openai_config(self) -> Dict[str, str]:
        """获取OpenAI配置"""
        return self.get('openai', {})

    def get_app_config(self) -> Dict[str, str]:
        """获取应用配置"""
        return self.get('app', {})


# 全局配置管理器实例
config_manager = ConfigManager()
