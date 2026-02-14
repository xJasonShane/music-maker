"""
历史记录管理模块 - 管理创作历史记录
"""
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from .exceptions import FileException


class HistoryManager:
    """历史记录管理器 - 管理创作历史记录"""

    def __init__(self, history_file: str = "./history.json"):
        """
        初始化历史记录管理器

        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = Path(history_file)
        self._history: List[Dict[str, Any]] = []
        self._next_id = 1
        self._load_history()
        self._next_id = self._get_max_id() + 1

    def _get_max_id(self) -> int:
        """获取当前最大ID"""
        if not self._history:
            return 0
        return max((r.get('id', 0) for r in self._history), default=0)

    def _load_history(self) -> None:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._history = json.load(f)
            except Exception as e:
                raise FileException("加载历史记录失败", str(e))
        else:
            self._history = []

    def _save_history(self) -> None:
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise FileException("保存历史记录失败", str(e))

    def add_record(self, record: Dict[str, Any]) -> None:
        """
        添加历史记录

        Args:
            record: 记录字典，包含创作信息
        """
        record['id'] = self._next_id
        self._next_id += 1
        record['created_at'] = datetime.now().isoformat()

        self._history.insert(0, record)
        self._save_history()

    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        获取所有历史记录

        Returns:
            历史记录列表
        """
        return self._history

    def get_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取历史记录

        Args:
            record_id: 记录ID

        Returns:
            记录字典，如果不存在则返回None
        """
        for record in self._history:
            if record.get('id') == record_id:
                return record
        return None

    def search_records(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索历史记录

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的记录列表
        """
        results = []
        keyword_lower = keyword.lower()

        for record in self._history:
            title = record.get('title', '').lower()
            prompt = record.get('prompt', '').lower()
            style = record.get('style', '').lower()

            if keyword_lower in title or keyword_lower in prompt or keyword_lower in style:
                results.append(record)

        return results

    def filter_by_type(self, creation_type: str) -> List[Dict[str, Any]]:
        """
        根据创作类型过滤历史记录

        Args:
            creation_type: 创作类型（lyrics/melody/arrangement）

        Returns:
            匹配的记录列表
        """
        return [r for r in self._history if r.get('type') == creation_type]

    def delete_record(self, record_id: int) -> bool:
        """
        删除历史记录

        Args:
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        for i, record in enumerate(self._history):
            if record.get('id') == record_id:
                self._history.pop(i)
                self._save_history()
                return True
        return False

    def clear_all(self) -> None:
        """清空所有历史记录"""
        self._history = []
        self._save_history()

    def get_recent_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的历史记录

        Args:
            limit: 返回记录数量

        Returns:
            最近的记录列表
        """
        return self._history[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        total = len(self._history)
        lyrics_count = len(self.filter_by_type('lyrics'))
        melody_count = len(self.filter_by_type('melody'))
        arrangement_count = len(self.filter_by_type('arrangement'))

        return {
            'total': total,
            'lyrics': lyrics_count,
            'melody': melody_count,
            'arrangement': arrangement_count
        }
