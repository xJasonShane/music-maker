"""
生成器管理模块 - 支持多模型切换
"""
from typing import Dict, Any, Optional, List
from .base import BaseAIGenerator
from .openai_client import OpenAIClient
from ..core.exceptions import APIException, ValidationException


class MockGenerator(BaseAIGenerator):
    """模拟生成器 - 用于演示，无需API密钥"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    def generate_lyrics(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """模拟生成歌词"""
        self._validate_prompt(prompt)
        
        style = kwargs.get('style', '流行')
        language = kwargs.get('language', '中文')
        
        lyrics = f"""【{style}风格歌词示例】

主歌：
在这个美好的时光里
阳光洒在大地上
微风轻轻吹过
带来无限的希望

副歌：
哦~ 这是一首{style}的旋律
跳动在我心底
让我们一起歌唱
感受音乐的魔力

主歌：
跟着节奏摇摆
放下所有烦恼
音乐让我们相遇
在这美好时刻

副歌：
哦~ 这是一首{style}的旋律
跳动在我心底
让我们一起歌唱
感受音乐的魔力

(生成提示：以上是模拟结果，配置API密钥后可获得真实AI创作"""
        
        metadata = {
            'model': 'Mock Generator',
            'style': style,
            'language': language,
            'tokens_used': 0
        }
        
        return self._format_result('lyrics', lyrics, metadata)
    
    def generate_melody(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """模拟生成旋律"""
        self._validate_prompt(prompt)
        
        notes = [
            {'pitch': 60, 'start_time': 0, 'duration': 0.5, 'velocity': 80},
            {'pitch': 62, 'start_time': 0.5, 'duration': 0.5, 'velocity': 80},
            {'pitch': 64, 'start_time': 1, 'duration': 0.5, 'velocity': 80},
            {'pitch': 65, 'start_time': 1.5, 'duration': 0.5, 'velocity': 80},
            {'pitch': 67, 'start_time': 2, 'duration': 1, 'velocity': 85}
        ]
        
        metadata = {
            'model': 'Mock Generator',
            'style': kwargs.get('style', '流行'),
            'tempo': kwargs.get('tempo', 120),
            'duration': kwargs.get('duration', 30),
            'notes_count': len(notes)
        }
        
        return self._format_result('melody', notes, metadata)
    
    def generate_arrangement(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """模拟生成编曲"""
        self._validate_prompt(prompt)
        
        arrangement = {
            'tracks': [
                {'name': '主旋律', 'notes': []},
                {'name': '贝斯', 'notes': []}
            ]
        }
        
        metadata = {
            'model': 'Mock Generator',
            'style': kwargs.get('style', '流行'),
            'tempo': kwargs.get('tempo', 120),
            'duration': kwargs.get('duration', 60),
            'tracks_count': len(arrangement['tracks'])
        }
        
        return self._format_result('arrangement', arrangement, metadata)


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

        has_valid_generator = False
        
        for model_id, model_config in models_config.items():
            if model_config.get('enabled', False) and model_config.get('api_key'):
                try:
                    generator = self._create_generator(model_id, model_config)
                    if generator:
                        self.register_generator(model_id, generator)
                        has_valid_generator = True
                except Exception as e:
                    print(f"创建生成器 {model_id} 失败: {e}")
        
        if not has_valid_generator:
            mock_config = {'name': '演示模式'}
            self.register_generator('mock', MockGenerator(mock_config))
            current_model = 'mock'
            print("未找到已配置的AI模型，启用演示模式")

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
