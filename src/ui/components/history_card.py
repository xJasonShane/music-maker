"""
历史记录卡片组件 - 显示单条历史记录
"""
import flet as ft
from typing import Dict, Any, Callable, Optional
from ..theme import DesignSystem


class HistoryCard:
    """
    历史记录卡片组件
    
    显示单条历史记录的摘要信息，
    支持点击查看详情。
    """
    
    _TYPE_MAP = {
        'lyrics': ('歌词', DesignSystem.Colors.SUCCESS_LIGHT),
        'melody': ('旋律', DesignSystem.Colors.PRIMARY_LIGHT),
        'arrangement': ('编曲', DesignSystem.Colors.WARNING_LIGHT)
    }
    
    def __init__(
        self,
        record: Dict[str, Any],
        on_click: Optional[Callable[[int], None]] = None
    ):
        """
        初始化历史记录卡片
        
        Args:
            record: 历史记录数据
            on_click: 点击回调函数
        """
        self._record = record
        self._on_click = on_click
        self._card = self._build()
    
    def _build(self) -> ft.Container:
        """构建卡片组件"""
        record_id = self._record.get('id', 0)
        prompt = self._record.get('prompt', '')
        result_type = self._record.get('type', 'lyrics')
        created_at = self._record.get('created_at', '')
        style = self._record.get('style', '流行')
        
        type_text, type_bgcolor = self._TYPE_MAP.get(
            result_type, 
            (result_type, DesignSystem.Colors.GREY_100)
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            f"#{record_id}",
                            weight=ft.FontWeight.BOLD,
                            size=16
                        ),
                        padding=ft.padding.symmetric(
                            horizontal=DesignSystem.Spacing.SM,
                            vertical=DesignSystem.Spacing.XS
                        ),
                        bgcolor=DesignSystem.Colors.PRIMARY_LIGHT,
                        border_radius=DesignSystem.Radius.SM
                    ),
                    ft.Container(
                        content=ft.Text(
                            type_text,
                            size=14,
                            weight=ft.FontWeight.W_500
                        ),
                        padding=ft.padding.symmetric(
                            horizontal=DesignSystem.Spacing.SM,
                            vertical=DesignSystem.Spacing.XS
                        ),
                        bgcolor=type_bgcolor,
                        border_radius=DesignSystem.Radius.SM
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        created_at[:19] if created_at else '',
                        size=12,
                        color=DesignSystem.Colors.TEXT_SECONDARY
                    )
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Text(
                        prompt[:120] + '...' if len(prompt) > 120 else prompt,
                        size=15,
                        color=DesignSystem.Colors.TEXT_PRIMARY,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    padding=ft.padding.symmetric(vertical=DesignSystem.Spacing.SM)
                ),
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            f"风格: {style}",
                            size=13,
                            color=DesignSystem.Colors.TEXT_SECONDARY
                        ),
                        padding=ft.padding.symmetric(
                            horizontal=DesignSystem.Spacing.SM,
                            vertical=DesignSystem.Spacing.XS
                        ),
                        bgcolor=DesignSystem.Colors.GREY_100,
                        border_radius=DesignSystem.Radius.SM
                    )
                ])
            ], spacing=DesignSystem.Spacing.MD),
            padding=DesignSystem.Spacing.XL,
            border_radius=DesignSystem.Radius.LG,
            bgcolor=DesignSystem.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            ),
            on_click=lambda e: self._handle_click(),
            ink=True
        )
    
    def _handle_click(self) -> None:
        """处理点击事件"""
        if self._on_click:
            record_id = self._record.get('id')
            self._on_click(record_id)
    
    @property
    def component(self) -> ft.Container:
        """获取组件实例"""
        return self._card
