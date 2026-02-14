"""
加载遮罩组件 - 显示加载状态
"""
import flet as ft
from typing import Optional
from ..theme import DesignSystem


class LoadingOverlay:
    """
    加载遮罩组件
    
    显示加载动画和提示文字，
    用于长时间操作时的用户反馈。
    """
    
    def __init__(self, message: str = "正在处理..."):
        """
        初始化加载遮罩
        
        Args:
            message: 加载提示文字
        """
        self._message = message
        self._visible = False
        self._indicator = ft.ProgressRing(
            width=48,
            height=48,
            stroke_width=4,
            color=DesignSystem.Colors.PRIMARY
        )
        self._text = ft.Text(
            message,
            size=16,
            color=DesignSystem.Colors.TEXT_SECONDARY
        )
        self._overlay = self._build()
    
    def _build(self) -> ft.Container:
        """构建遮罩组件"""
        return ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                ft.Column([
                    self._indicator,
                    self._text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(expand=True)
            ], expand=True),
            bgcolor=ft.Colors.with_opacity(0.9, DesignSystem.Colors.WHITE),
            visible=self._visible,
            expand=True
        )
    
    @property
    def component(self) -> ft.Container:
        """获取组件实例"""
        return self._overlay
    
    def show(self, message: Optional[str] = None) -> None:
        """
        显示遮罩
        
        Args:
            message: 可选的新提示文字
        """
        if message:
            self._message = message
            self._text.value = message
        self._visible = True
        self._overlay.visible = True
    
    def hide(self) -> None:
        """隐藏遮罩"""
        self._visible = False
        self._overlay.visible = False
    
    def set_message(self, message: str) -> None:
        """
        设置提示文字
        
        Args:
            message: 新的提示文字
        """
        self._message = message
        self._text.value = message
    
    @property
    def is_visible(self) -> bool:
        """获取可见状态"""
        return self._visible
