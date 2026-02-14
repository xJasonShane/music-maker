"""
导出服务 - 统一文件导出逻辑
封装歌词、音频等文件的导出功能
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ExportService:
    """
    导出服务 - 统一文件导出逻辑
    
    提供歌词、音频等文件的导出功能，
    支持自定义输出目录和文件命名。
    """
    
    def __init__(self, output_dir: str = './output'):
        """
        初始化导出服务
        
        Args:
            output_dir: 输出目录路径
        """
        self._output_dir = Path(output_dir)
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """确保输出目录存在"""
        self._output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, prefix: str, extension: str) -> str:
        """
        生成带时间戳的文件名
        
        Args:
            prefix: 文件名前缀
            extension: 文件扩展名
        
        Returns:
            生成的文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_lyrics(
        self, 
        lyrics: str, 
        filename: Optional[str] = None,
        encoding: str = 'utf-8'
    ) -> Dict[str, Any]:
        """
        导出歌词文件
        
        Args:
            lyrics: 歌词内容
            filename: 自定义文件名（可选）
            encoding: 文件编码
        
        Returns:
            导出结果字典，包含success、filepath、message等字段
        """
        if not lyrics or not lyrics.strip():
            return {
                'success': False,
                'filepath': None,
                'message': '歌词内容为空，无法导出'
            }
        
        try:
            self._ensure_output_dir()
            
            if not filename:
                filename = self._generate_filename('lyrics', 'txt')
            
            filepath = self._output_dir / filename
            
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(lyrics)
            
            logger.info(f"歌词已导出到: {filepath}")
            
            return {
                'success': True,
                'filepath': str(filepath),
                'filename': filename,
                'message': f'歌词已保存: {filename}'
            }
            
        except PermissionError as e:
            logger.error(f"导出歌词失败（权限错误）: {e}")
            return {
                'success': False,
                'filepath': None,
                'message': '导出失败：没有写入权限'
            }
        except Exception as e:
            logger.error(f"导出歌词失败: {e}", exc_info=True)
            return {
                'success': False,
                'filepath': None,
                'message': f'导出失败: {str(e)}'
            }
    
    def export_all(
        self,
        lyrics: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        一键导出所有内容
        
        Args:
            lyrics: 歌词内容
            audio_data: 音频数据
            metadata: 元数据
        
        Returns:
            导出结果字典
        """
        results = {
            'success': True,
            'files': [],
            'messages': []
        }
        
        if lyrics:
            lyrics_result = self.export_lyrics(lyrics)
            if lyrics_result['success']:
                results['files'].append(lyrics_result['filepath'])
                results['messages'].append(lyrics_result['message'])
            else:
                results['success'] = False
                results['messages'].append(lyrics_result['message'])
        
        if audio_data:
            audio_result = self._export_audio(audio_data, metadata)
            if audio_result['success']:
                results['files'].append(audio_result['filepath'])
                results['messages'].append(audio_result['message'])
            else:
                results['success'] = False
                results['messages'].append(audio_result['message'])
        
        return results
    
    def _export_audio(
        self,
        audio_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        导出音频文件
        
        Args:
            audio_data: 音频数据
            metadata: 元数据
        
        Returns:
            导出结果字典
        """
        try:
            self._ensure_output_dir()
            
            filename = self._generate_filename('music', 'wav')
            filepath = self._output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"音频已导出到: {filepath}")
            
            return {
                'success': True,
                'filepath': str(filepath),
                'filename': filename,
                'message': f'音频已保存: {filename}'
            }
            
        except Exception as e:
            logger.error(f"导出音频失败: {e}", exc_info=True)
            return {
                'success': False,
                'filepath': None,
                'message': f'导出音频失败: {str(e)}'
            }
    
    def set_output_dir(self, output_dir: str) -> None:
        """
        设置输出目录
        
        Args:
            output_dir: 新的输出目录路径
        """
        self._output_dir = Path(output_dir)
        self._ensure_output_dir()
    
    def get_output_dir(self) -> Path:
        """
        获取当前输出目录
        
        Returns:
            输出目录路径
        """
        return self._output_dir
