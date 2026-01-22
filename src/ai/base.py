"""
AI创作基类 - 定义统一的AI创作接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAIGenerator(ABC):
    """AI生成器基类 - 定义统一的生成接口"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI生成器

        Args:
            config: 配置字典
        """
        self.config = config

    @abstractmethod
    def generate_lyrics(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成歌词

        Args:
            prompt: 提示词
            **kwargs: 自定义参数（风格、语言等）

        Returns:
            生成结果字典，包含歌词文本和元数据
        """
        pass

    @abstractmethod
    def generate_melody(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成旋律（MIDI格式）

        Args:
            prompt: 提示词
            **kwargs: 自定义参数（风格、节拍、时长等）

        Returns:
            生成结果字典，包含MIDI数据和元数据
        """
        pass

    @abstractmethod
    def generate_arrangement(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成完整编曲

        Args:
            prompt: 提示词
            **kwargs: 自定义参数（风格、节拍、时长等）

        Returns:
            生成结果字典，包含编曲数据和元数据
        """
        pass

    def _validate_prompt(self, prompt: str) -> None:
        """
        验证提示词

        Args:
            prompt: 提示词

        Raises:
            ValueError: 提示词为空或无效
        """
        if not prompt or not prompt.strip():
            raise ValueError("提示词不能为空")

    def _format_result(self, result_type: str, data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化生成结果

        Args:
            result_type: 结果类型（lyrics/melody/arrangement）
            data: 生成数据
            metadata: 元数据

        Returns:
            格式化的结果字典
        """
        return {
            'type': result_type,
            'data': data,
            'metadata': metadata,
            'success': True
        }
