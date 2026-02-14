"""
消息服务 - 统一消息提示
封装SnackBar创建逻辑，提供统一的消息展示接口
"""
import flet as ft
from enum import Enum
from typing import Optional


class MessageType(Enum):
    """消息类型枚举"""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class MessageService:
    """
    消息提示服务 - 统一消息展示
    
    提供success、error、info、warning四种消息类型，
    内部封装SnackBar创建逻辑，消除重复代码。
    """
    
    _MESSAGE_CONFIG = {
        MessageType.SUCCESS: {
            'icon': ft.icons.Icons.CHECK_CIRCLE,
            'bgcolor': ft.Colors.GREEN_600,
            'duration': 3000
        },
        MessageType.ERROR: {
            'icon': ft.icons.Icons.ERROR,
            'bgcolor': ft.Colors.RED_600,
            'duration': 4000
        },
        MessageType.INFO: {
            'icon': ft.icons.Icons.INFO,
            'bgcolor': ft.Colors.BLUE_600,
            'duration': 3000
        },
        MessageType.WARNING: {
            'icon': ft.icons.Icons.WARNING,
            'bgcolor': ft.Colors.ORANGE_600,
            'duration': 3500
        }
    }
    
    def __init__(self, page: ft.Page):
        """
        初始化消息服务
        
        Args:
            page: Flet页面对象
        """
        self._page = page
    
    def show(self, message: str, msg_type: MessageType = MessageType.INFO) -> None:
        """
        显示消息
        
        Args:
            message: 消息内容
            msg_type: 消息类型
        """
        config = self._MESSAGE_CONFIG.get(msg_type, self._MESSAGE_CONFIG[MessageType.INFO])
        
        snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(config['icon'], color=ft.Colors.WHITE, size=20),
                ft.Text(message, color=ft.Colors.WHITE, size=14)
            ], spacing=10),
            bgcolor=config['bgcolor'],
            duration=config['duration']
        )
        
        self._page.snack_bar = snack_bar
        snack_bar.open = True
        self._page.update()
    
    def success(self, message: str) -> None:
        """
        显示成功消息
        
        Args:
            message: 消息内容
        """
        self.show(message, MessageType.SUCCESS)
    
    def error(self, message: str) -> None:
        """
        显示错误消息
        
        Args:
            message: 消息内容
        """
        self.show(message, MessageType.ERROR)
    
    def info(self, message: str) -> None:
        """
        显示信息消息
        
        Args:
            message: 消息内容
        """
        self.show(message, MessageType.INFO)
    
    def warning(self, message: str) -> None:
        """
        显示警告消息
        
        Args:
            message: 消息内容
        """
        self.show(message, MessageType.WARNING)
