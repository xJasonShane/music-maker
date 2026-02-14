"""
AI生成器工厂 - 支持动态注册和创建AI生成器
使用工厂模式解耦生成器创建逻辑
"""
import logging
from typing import Dict, Any, Optional, Type

from .base import BaseAIGenerator

logger = logging.getLogger(__name__)


class AIGeneratorFactory:
    """
    AI生成器工厂 - 支持动态注册和创建
    
    使用工厂模式管理AI生成器的创建，
    支持动态注册新的生成器类型，
    实现生成器创建与使用的解耦。
    """
    
    _registry: Dict[str, Type[BaseAIGenerator]] = {}
    
    @classmethod
    def register(cls, model_id: str, generator_class: Type[BaseAIGenerator]) -> None:
        """
        注册生成器类型
        
        Args:
            model_id: 模型标识符
            generator_class: 生成器类
        """
        cls._registry[model_id] = generator_class
        logger.info(f"已注册AI生成器: {model_id}")
    
    @classmethod
    def unregister(cls, model_id: str) -> bool:
        """
        注销生成器类型
        
        Args:
            model_id: 模型标识符
        
        Returns:
            是否注销成功
        """
        if model_id in cls._registry:
            del cls._registry[model_id]
            logger.info(f"已注销AI生成器: {model_id}")
            return True
        return False
    
    @classmethod
    def create(cls, model_id: str, config: Dict[str, Any]) -> Optional[BaseAIGenerator]:
        """
        创建生成器实例
        
        Args:
            model_id: 模型标识符
            config: 生成器配置
        
        Returns:
            生成器实例，如果创建失败则返回None
        """
        generator_class = cls._registry.get(model_id)
        
        if generator_class is None:
            logger.warning(f"未找到注册的生成器: {model_id}")
            return None
        
        try:
            generator = generator_class(config)
            logger.info(f"成功创建生成器实例: {model_id}")
            return generator
        except Exception as e:
            logger.error(f"创建生成器 {model_id} 失败: {e}")
            return None
    
    @classmethod
    def is_registered(cls, model_id: str) -> bool:
        """
        检查生成器是否已注册
        
        Args:
            model_id: 模型标识符
        
        Returns:
            是否已注册
        """
        return model_id in cls._registry
    
    @classmethod
    def get_registered_models(cls) -> list:
        """
        获取所有已注册的模型ID
        
        Returns:
            模型ID列表
        """
        return list(cls._registry.keys())
    
    @classmethod
    def clear_registry(cls) -> None:
        """清空注册表"""
        cls._registry.clear()
        logger.info("已清空所有注册的AI生成器")


def register_builtin_generators() -> None:
    """注册内置的AI生成器"""
    from .openai_client import OpenAIClient
    from .generator import MockGenerator
    
    AIGeneratorFactory.register('openai', OpenAIGenerator)
    AIGeneratorFactory.register('claude', OpenAIGenerator)
    AIGeneratorFactory.register('qianwen', OpenAIGenerator)
    AIGeneratorFactory.register('ernie', OpenAIGenerator)
    AIGeneratorFactory.register('mock', MockGenerator)
    
    logger.info("已注册所有内置AI生成器")


class OpenAIGenerator(BaseAIGenerator):
    """
    OpenAI兼容生成器
    
    支持所有兼容OpenAI API的服务，
    包括OpenAI、Claude、通义千问等。
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from .openai_client import OpenAIClient
        self._client = OpenAIClient(config)
    
    def generate_lyrics(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return self._client.generate_lyrics(prompt, **kwargs)
    
    def generate_melody(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return self._client.generate_melody(prompt, **kwargs)
    
    def generate_arrangement(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return self._client.generate_arrangement(prompt, **kwargs)
