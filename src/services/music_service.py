"""
音乐服务 - 音乐创作业务逻辑
封装歌词生成、旋律创作等核心业务逻辑
"""
import logging
import threading
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class MusicService:
    """
    音乐服务 - 音乐创作业务逻辑
    
    封装歌词生成、旋律创作等核心业务逻辑，
    提供异步生成支持，解耦UI与AI生成器。
    """
    
    def __init__(self, generator_manager):
        """
        初始化音乐服务
        
        Args:
            generator_manager: AI生成器管理器
        """
        self._generator_manager = generator_manager
    
    def generate_lyrics(
        self,
        prompt: str,
        style: str = '流行',
        language: str = '中文',
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        异步生成歌词
        
        Args:
            prompt: 创作提示词
            style: 音乐风格
            language: 歌词语言
            on_complete: 完成回调
            on_error: 错误回调
        """
        def _generate():
            try:
                logger.info(f"开始生成歌词: {prompt[:50]}...")
                result = self._generator_manager.generate_lyrics(
                    prompt,
                    style=style,
                    language=language
                )
                if on_complete:
                    on_complete(result)
            except Exception as ex:
                logger.error(f"生成歌词失败: {ex}", exc_info=True)
                if on_error:
                    on_error(str(ex))
        
        thread = threading.Thread(target=_generate)
        thread.daemon = True
        thread.start()
    
    def generate_lyrics_sync(
        self,
        prompt: str,
        style: str = '流行',
        language: str = '中文'
    ) -> Dict[str, Any]:
        """
        同步生成歌词
        
        Args:
            prompt: 创作提示词
            style: 音乐风格
            language: 歌词语言
        
        Returns:
            生成结果字典
        """
        logger.info(f"同步生成歌词: {prompt[:50]}...")
        return self._generator_manager.generate_lyrics(
            prompt,
            style=style,
            language=language
        )
    
    def generate_melody(
        self,
        prompt: str,
        style: str = '流行',
        tempo: int = 120,
        duration: int = 30,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        异步生成旋律
        
        Args:
            prompt: 创作提示词
            style: 音乐风格
            tempo: 节拍BPM
            duration: 时长秒数
            on_complete: 完成回调
            on_error: 错误回调
        """
        def _generate():
            try:
                logger.info(f"开始生成旋律: {prompt[:50]}...")
                result = self._generator_manager.generate_melody(
                    prompt,
                    style=style,
                    tempo=tempo,
                    duration=duration
                )
                if on_complete:
                    on_complete(result)
            except Exception as ex:
                logger.error(f"生成旋律失败: {ex}", exc_info=True)
                if on_error:
                    on_error(str(ex))
        
        thread = threading.Thread(target=_generate)
        thread.daemon = True
        thread.start()
    
    def validate_prompt(self, prompt: str) -> tuple:
        """
        验证提示词
        
        Args:
            prompt: 用户输入的提示词
        
        Returns:
            (is_valid, error_message) 元组
        """
        if not prompt or not prompt.strip():
            return False, "请输入提示词"
        if len(prompt.strip()) < 5:
            return False, "提示词太短，请至少输入 5 个字符"
        if len(prompt) > 2000:
            return False, "提示词太长，请控制在 2000 字符以内"
        return True, ""
    
    def get_available_models(self) -> list:
        """
        获取可用的模型列表
        
        Returns:
            模型ID列表
        """
        return self._generator_manager.get_available_generators()
    
    def set_current_model(self, model_id: str) -> bool:
        """
        设置当前使用的模型
        
        Args:
            model_id: 模型ID
        
        Returns:
            是否设置成功
        """
        try:
            self._generator_manager.set_current_generator(model_id)
            return True
        except Exception:
            return False
