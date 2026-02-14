"""
配置管理模块 - 支持多模型配置
"""
import os
import json
import logging
import threading
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器 - 支持多模型配置"""

    _instance = None
    _initialized = False
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config: Dict[str, Any] = {}
        self._env_path: Optional[Path] = None
        self._config_path: Optional[Path] = None
        self._initialized = True

    def load_config(self, env_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            env_path: .env文件路径，默认为项目根目录下的.env

        Returns:
            配置字典
        """
        if env_path:
            self._env_path = Path(env_path)
        else:
            self._env_path = Path(__file__).parent.parent.parent / '.env'

        self._config_path = Path(__file__).parent.parent.parent / 'config.json'

        if not self._env_path.exists():
            self._env_path.touch()

        load_dotenv(self._env_path)

        self._config = self._load_default_config()

        if self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self._config.update(saved_config)
            except json.JSONDecodeError as e:
                logger.warning(f"配置文件JSON格式错误，使用默认配置: {e}")
            except PermissionError as e:
                logger.warning(f"无法读取配置文件，使用默认配置: {e}")
            except Exception as e:
                logger.warning(f"加载配置文件失败，使用默认配置: {e}")

        return self._config

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            'models': {
                'openai': {
                    'name': 'OpenAI',
                    'api_key': '',
                    'api_base': 'https://api.openai.com/v1',
                    'model': 'gpt-4',
                    'enabled': True
                },
                'claude': {
                    'name': 'Claude',
                    'api_key': '',
                    'api_base': 'https://api.anthropic.com/v1',
                    'model': 'claude-3-opus-20240229',
                    'enabled': False
                },
                'qianwen': {
                    'name': '通义千问',
                    'api_key': '',
                    'api_base': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                    'model': 'qwen-max',
                    'enabled': False
                },
                'ernie': {
                    'name': '文心一言',
                    'api_key': '',
                    'api_base': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop',
                    'model': 'ernie-bot-4',
                    'enabled': False
                }
            },
            'current_model': 'openai',
            'app': {
                'output_dir': os.getenv('OUTPUT_DIR', './output'),
                'history_file': os.getenv('HISTORY_FILE', './history.json')
            }
        }

    def save_config(self, config: Dict[str, Any]) -> None:
        """
        保存配置到文件

        Args:
            config: 配置字典
        """
        if not self._config_path:
            self._config_path = Path(__file__).parent.parent.parent / 'config.json'

        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        self._config = config

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键（如 'models.openai.api_key'）
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

    def get_models_config(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模型配置"""
        return self.get('models', {})

    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型配置

        Args:
            model_id: 模型ID

        Returns:
            模型配置字典
        """
        return self.get(f'models.{model_id}')

    def set_model_config(self, model_id: str, config: Dict[str, Any]) -> None:
        """
        设置指定模型配置

        Args:
            model_id: 模型ID
            config: 模型配置
        """
        self.set(f'models.{model_id}', config)

    def get_current_model(self) -> str:
        """获取当前使用的模型ID"""
        return self.get('current_model', 'openai')

    def set_current_model(self, model_id: str) -> None:
        """
        设置当前使用的模型

        Args:
            model_id: 模型ID
        """
        self.set('current_model', model_id)

    def get_enabled_models(self) -> List[str]:
        """获取已启用的模型ID列表"""
        models = self.get_models_config()
        return [model_id for model_id, config in models.items() if config.get('enabled', False)]

    def get_app_config(self) -> Dict[str, str]:
        """获取应用配置"""
        return self.get('app', {})


# 全局配置管理器实例
config_manager = ConfigManager()
