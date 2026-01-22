"""
生成器管理模块 - 支持多模型切换
"""
from typing import Dict, Any, Optional, List
from .base import BaseAIGenerator
from .openai_client import OpenAIClient
from ..core.exceptions import APIException, ValidationException


class GeneratorManager:
    """生成器管理器 - 支持多模型切换"""

    def __init__(self):
        """初始化生成器管理器"""
        self._generators: Dict[str, BaseAIGenerator] = {}
        self._current_generator: Optional[BaseAIGenerator] = None
        self._config: Dict[str, Any] = {}

    def register_generator(self, name: str, generator: BaseAIGenerator) -> None:
        """
        注册AI生成器

        Args:
            name: 生成器名称
            generator: 生成器实例
        """
        self._generators[name] = generator

    def set_current_generator(self, name: str) -> None:
        """
        设置当前使用的生成器

        Args:
            name: 生成器名称

        Raises:
            ValueError: 生成器不存在
        """
        if name not in self._generators:
            raise ValueError(f"生成器 '{name}' 不存在")
        self._current_generator = self._generators[name]

    def get_current_generator(self) -> BaseAIGenerator:
        """
        获取当前生成器

        Returns:
            当前生成器实例

        Raises:
            ValueError: 未设置当前生成器
        """
        if self._current_generator is None:
            raise ValueError("未设置当前生成器")
        return self._current_generator

    def get_available_generators(self) -> List[str]:
        """
        获取可用的生成器列表

        Returns:
            生成器名称列表
        """
        return list(self._generators.keys())

    def generate_lyrics(self, prompt: str, generator_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        生成歌词

        Args:
            prompt: 提示词
            generator_name: 生成器名称，如果为None则使用当前生成器
            **kwargs: 自定义参数

        Returns:
            生成结果字典
        """
        generator = self._get_generator(generator_name)
        return generator.generate_lyrics(prompt, **kwargs)

    def generate_melody(self, prompt: str, generator_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        生成旋律

        Args:
            prompt: 提示词
            generator_name: 生成器名称，如果为None则使用当前生成器
            **kwargs: 自定义参数

        Returns:
            生成结果字典
        """
        generator = self._get_generator(generator_name)
        return generator.generate_melody(prompt, **kwargs)

    def generate_arrangement(self, prompt: str, generator_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        生成编曲

        Args:
            prompt: 提示词
            generator_name: 生成器名称，如果为None则使用当前生成器
            **kwargs: 自定义参数

        Returns:
            生成结果字典
        """
        generator = self._get_generator(generator_name)
        return generator.generate_arrangement(prompt, **kwargs)

    def _get_generator(self, generator_name: Optional[str] = None) -> BaseAIGenerator:
        """
        获取生成器

        Args:
            generator_name: 生成器名称

        Returns:
            生成器实例

        Raises:
            ValueError: 生成器不存在
        """
        if generator_name:
            if generator_name not in self._generators:
                raise ValueError(f"生成器 '{generator_name}' 不存在")
            return self._generators[generator_name]
        elif self._current_generator:
            return self._current_generator
        else:
            raise ValueError("未设置当前生成器")

    def create_from_config(self, config: Dict[str, Any]) -> None:
        """
        根据配置创建生成器

        Args:
            config: 配置字典
        """
        self._config = config
        models_config = config.get('models', {})
        current_model = config.get('current_model', 'openai')

        self._generators.clear()

        for model_id, model_config in models_config.items():
            if not model_config.get('enabled', False):
                continue

            if not model_config.get('api_key'):
                continue

            try:
                generator = self._create_generator(model_id, model_config)
                if generator:
                    self.register_generator(model_id, generator)
            except Exception as e:
                print(f"创建生成器 {model_id} 失败: {e}")

        if current_model in self._generators:
            self.set_current_generator(current_model)
        elif self._generators:
            first_available = list(self._generators.keys())[0]
            self.set_current_generator(first_available)

    def _create_generator(self, model_id: str, model_config: Dict[str, Any]) -> Optional[BaseAIGenerator]:
        """
        创建生成器实例

        Args:
            model_id: 模型ID
            model_config: 模型配置

        Returns:
            生成器实例
        """
        try:
            return OpenAIClient(model_config)
        except Exception as e:
            print(f"创建 {model_id} 生成器失败: {e}")
            return None

    def update_generator_config(self, model_id: str, model_config: Dict[str, Any]) -> None:
        """
        更新生成器配置

        Args:
            model_id: 模型ID
            model_config: 模型配置
        """
        if model_id in self._generators:
            del self._generators[model_id]

        if model_config.get('enabled', False) and model_config.get('api_key'):
            try:
                generator = self._create_generator(model_id, model_config)
                if generator:
                    self.register_generator(model_id, generator)
                    if model_id == self._config.get('current_model'):
                        self.set_current_generator(model_id)
            except Exception as e:
                print(f"更新生成器 {model_id} 失败: {e}")

    def convert_to_standard_format(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将生成结果转换为标准格式

        Args:
            result: 生成结果

        Returns:
            标准格式结果
        """
        if not result.get('success', False):
            return {
                'success': False,
                'error': result.get('error', '生成失败')
            }

        result_type = result.get('type', '')
        data = result.get('data', {})
        metadata = result.get('metadata', {})

        standard_result = {
            'success': True,
            'type': result_type,
            'metadata': metadata
        }

        if result_type == 'lyrics':
            standard_result['lyrics'] = data
            standard_result['format'] = 'text'

        elif result_type == 'melody':
            standard_result['notes'] = data
            standard_result['format'] = 'midi'

        elif result_type == 'arrangement':
            standard_result['tracks'] = data.get('tracks', [])
            standard_result['format'] = 'midi'

        return standard_result
