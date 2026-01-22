"""
文件管理模块 - 处理音频文件的保存和加载
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from midiutil import MIDIFile
from .exceptions import FileException


class FileManager:
    """文件管理器 - 处理音频文件的保存和加载"""

    def __init__(self, output_dir: str = "./output"):
        """
        初始化文件管理器

        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """确保输出目录存在"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_midi(self, midi_data: bytes, filename: Optional[str] = None) -> str:
        """
        保存MIDI文件

        Args:
            midi_data: MIDI二进制数据
            filename: 文件名，如果不提供则自动生成

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"music_{timestamp}.mid"

        filepath = self.output_dir / filename

        try:
            with open(filepath, 'wb') as f:
                f.write(midi_data)
            return str(filepath)
        except Exception as e:
            raise FileException("保存MIDI文件失败", str(e))

    def create_midi_from_notes(self, notes: list, filename: Optional[str] = None) -> str:
        """
        从音符列表创建MIDI文件

        Args:
            notes: 音符列表，格式为 [(pitch, start_time, duration, velocity), ...]
            filename: 文件名

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"music_{timestamp}.mid"

        filepath = self.output_dir / filename

        try:
            midi = MIDIFile(1)
            track = 0
            time = 0
            midi.addTrackName(track, time, "Track")
            midi.addTempo(track, time, 120)

            for pitch, start_time, duration, velocity in notes:
                midi.addNote(track, 0, pitch, start_time, duration, velocity)

            with open(filepath, 'wb') as f:
                midi.writeFile(f)
            return str(filepath)
        except Exception as e:
            raise FileException("创建MIDI文件失败", str(e))

    def save_mp3(self, mp3_data: bytes, filename: Optional[str] = None) -> str:
        """
        保存MP3文件

        Args:
            mp3_data: MP3二进制数据
            filename: 文件名

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"music_{timestamp}.mp3"

        filepath = self.output_dir / filename

        try:
            with open(filepath, 'wb') as f:
                f.write(mp3_data)
            return str(filepath)
        except Exception as e:
            raise FileException("保存MP3文件失败", str(e))

    def save_lyrics(self, lyrics: str, filename: Optional[str] = None) -> str:
        """
        保存歌词文件

        Args:
            lyrics: 歌词文本
            filename: 文件名

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lyrics_{timestamp}.txt"

        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(lyrics)
            return str(filepath)
        except Exception as e:
            raise FileException("保存歌词文件失败", str(e))

    def save_metadata(self, metadata: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        保存元数据文件

        Args:
            metadata: 元数据字典
            filename: 文件名

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metadata_{timestamp}.json"

        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            return str(filepath)
        except Exception as e:
            raise FileException("保存元数据文件失败", str(e))

    def load_file(self, filepath: str) -> bytes:
        """
        加载文件

        Args:
            filepath: 文件路径

        Returns:
            文件内容
        """
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            raise FileException("加载文件失败", str(e))

    def file_exists(self, filepath: str) -> bool:
        """
        检查文件是否存在

        Args:
            filepath: 文件路径

        Returns:
            文件是否存在
        """
        return Path(filepath).exists()

    def delete_file(self, filepath: str) -> None:
        """
        删除文件

        Args:
            filepath: 文件路径
        """
        try:
            Path(filepath).unlink()
        except Exception as e:
            raise FileException("删除文件失败", str(e))

    def get_output_dir(self) -> str:
        """获取输出目录路径"""
        return str(self.output_dir)
