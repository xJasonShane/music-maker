"""
发布基类 - 定义统一的发布接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePublisher(ABC):
    """发布器基类 - 定义统一的发布接口"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化发布器

        Args:
            config: 配置字典
        """
        self.config = config
        self._authenticated = False

    @abstractmethod
    def authenticate(self) -> bool:
        """
        认证

        Returns:
            是否认证成功
        """
        pass

    @abstractmethod
    def publish(self, title: str, audio_file: str, **kwargs) -> Dict[str, Any]:
        """
        发布音乐

        Args:
            title: 歌曲标题
            audio_file: 音频文件路径
            **kwargs: 其他参数（歌词、封面等）

        Returns:
            发布结果字典
        """
        pass

    def is_authenticated(self) -> bool:
        """
        检查是否已认证

        Returns:
            是否已认证
        """
        return self._authenticated

    def _validate_audio_file(self, audio_file: str) -> None:
        """
        验证音频文件

        Args:
            audio_file: 音频文件路径

        Raises:
            ValueError: 文件不存在或格式不支持
        """
        from pathlib import Path

        file_path = Path(audio_file)
        if not file_path.exists():
            raise ValueError(f"音频文件不存在: {audio_file}")

        supported_formats = ['.mp3', '.wav', '.flac', '.m4a']
        if file_path.suffix.lower() not in supported_formats:
            raise ValueError(f"不支持的音频格式: {file_path.suffix}")
