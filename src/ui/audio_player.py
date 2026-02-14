"""
音频播放器组件 - 现代化UI设计
采用设计系统，提升视觉体验
"""
import flet as ft
from typing import Optional, Callable
from .theme import DesignSystem


class AudioPlayer:
    """音频播放器组件 - 现代化UI设计"""

    def __init__(self, on_play_end: Optional[Callable] = None):
        """
        初始化音频播放器

        Args:
            on_play_end: 播放结束回调
        """
        self.on_play_end = on_play_end
        self._page = None
        self._current_file = None
        self._is_playing = False
        
        self._play_button = ft.IconButton(
            icon=ft.icons.Icons.PLAY_ARROW,
            tooltip="播放",
            icon_size=32,
            icon_color=DesignSystem.Colors.PRIMARY,
            bgcolor=DesignSystem.Colors.PRIMARY_LIGHT,
            on_click=self._on_play_click
        )
        self._pause_button = ft.IconButton(
            icon=ft.icons.Icons.PAUSE,
            tooltip="暂停",
            icon_size=32,
            icon_color=DesignSystem.Colors.PRIMARY,
            bgcolor=DesignSystem.Colors.PRIMARY_LIGHT,
            on_click=self._on_pause_click,
            visible=False
        )
        self._stop_button = ft.IconButton(
            icon=ft.icons.Icons.STOP,
            tooltip="停止",
            icon_size=28,
            icon_color=DesignSystem.Colors.ERROR,
            bgcolor=DesignSystem.Colors.ERROR_LIGHT,
            on_click=self._on_stop_click,
            visible=False
        )
        self._progress_slider = ft.Slider(
            min=0,
            max=100,
            value=0,
            disabled=True,
            expand=True,
            active_color=DesignSystem.Colors.PRIMARY,
            inactive_color=DesignSystem.Colors.GREY_300
        )
        self._time_label = ft.Text(
            "00:00 / 00:00", 
            size=12,
            color=DesignSystem.Colors.TEXT_SECONDARY
        )
        self._file_label = ft.Text(
            "未加载音频文件",
            size=14,
            color=DesignSystem.Colors.TEXT_DISABLED,
            text_align=ft.TextAlign.CENTER,
            expand=True
        )

    def build(self, page: ft.Page) -> ft.Container:
        """构建播放器UI"""
        self._page = page
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.icons.Icons.MUSIC_NOTE,
                            size=48,
                            color=DesignSystem.Colors.PRIMARY
                        ),
                        self._file_label
                    ], spacing=DesignSystem.Spacing.MD, alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.only(bottom=DesignSystem.Spacing.MD)
                ),
                ft.Container(
                    content=ft.Row([
                        self._play_button,
                        self._pause_button,
                        self._stop_button,
                        ft.Container(width=DesignSystem.Spacing.LG)
                    ], spacing=DesignSystem.Spacing.SM, alignment=ft.MainAxisAlignment.CENTER)
                ),
                ft.Container(height=DesignSystem.Spacing.SM),
                ft.Row([
                    self._progress_slider,
                    ft.Container(width=DesignSystem.Spacing.SM),
                    self._time_label
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=DesignSystem.Spacing.SM)
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
            padding=DesignSystem.Spacing.LG,
            border=ft.border.all(1, DesignSystem.Colors.GREY_200),
            border_radius=DesignSystem.Radius.MD,
            bgcolor=DesignSystem.Colors.WHITE
        )

    def load_audio(self, file_path: str) -> None:
        """
        加载音频文件

        Args:
            file_path: 音频文件路径
        """
        self._current_file = file_path
        self._progress_slider.disabled = False
        self._file_label.value = self._format_filename(file_path)
        self._file_label.color = DesignSystem.Colors.TEXT_PRIMARY
        self._update()

    def play(self) -> None:
        """播放音频"""
        if self._current_file:
            self._is_playing = True
            self._play_button.visible = False
            self._pause_button.visible = True
            self._stop_button.visible = True
            self._update()

    def pause(self) -> None:
        """暂停音频"""
        self._is_playing = False
        self._play_button.visible = True
        self._pause_button.visible = False
        self._update()

    def stop(self) -> None:
        """停止音频"""
        self._is_playing = False
        self._play_button.visible = True
        self._pause_button.visible = False
        self._stop_button.visible = False
        self._progress_slider.value = 0
        self._update()

    def _on_play_click(self, e) -> None:
        """播放按钮点击事件"""
        self.play()

    def _on_pause_click(self, e) -> None:
        """暂停按钮点击事件"""
        self.pause()

    def _on_stop_click(self, e) -> None:
        """停止按钮点击事件"""
        self.stop()

    def set_volume(self, volume: float) -> None:
        """
        设置音量

        Args:
            volume: 音量值（0.0-1.0）
        """
        pass

    def get_current_file(self) -> Optional[str]:
        """获取当前播放的文件"""
        return self._current_file

    def is_playing(self) -> bool:
        """检查是否正在播放"""
        return self._is_playing

    def _format_filename(self, file_path: str) -> str:
        """格式化文件名显示"""
        from pathlib import Path
        return Path(file_path).name

    def _update(self):
        """更新UI"""
        if self._page:
            self._page.update()
