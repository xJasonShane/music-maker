"""
音频播放器组件 - 支持MIDI/MP3播放
"""
import flet as ft
from typing import Optional, Callable


class AudioPlayer(ft.UserControl):
    """音频播放器组件"""

    def __init__(self, on_play_end: Optional[Callable] = None):
        """
        初始化音频播放器

        Args:
            on_play_end: 播放结束回调
        """
        super().__init__()
        self.on_play_end = on_play_end
        self._audio_player = ft.Audio(
            volume=1.0,
            balance=0.0,
            autoplay=False,
            release_mode=ft.AudioReleaseMode.RELEASE
        )
        self._play_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            tooltip="播放",
            on_click=self._on_play_click
        )
        self._pause_button = ft.IconButton(
            icon=ft.icons.PAUSE,
            tooltip="暂停",
            on_click=self._on_pause_click,
            visible=False
        )
        self._stop_button = ft.IconButton(
            icon=ft.icons.STOP,
            tooltip="停止",
            on_click=self._on_stop_click,
            visible=False
        )
        self._progress_slider = ft.Slider(
            min=0,
            max=100,
            value=0,
            disabled=True,
            expand=True
        )
        self._time_label = ft.Text("00:00 / 00:00", size=12)
        self._current_file = None

    def build(self):
        """构建播放器UI"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self._play_button,
                    self._pause_button,
                    self._stop_button,
                    self._progress_slider,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    ft.Container(expand=True),
                    self._time_label,
                    ft.Container(expand=True)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=5),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            bgcolor=ft.colors.GREY_50
        )

    def load_audio(self, file_path: str) -> None:
        """
        加载音频文件

        Args:
            file_path: 音频文件路径
        """
        self._current_file = file_path
        self._audio_player.src = file_path
        self._progress_slider.disabled = False

    def play(self) -> None:
        """播放音频"""
        if self._current_file:
            self._audio_player.play()
            self._play_button.visible = False
            self._pause_button.visible = True
            self._stop_button.visible = True
            self.update()

    def pause(self) -> None:
        """暂停音频"""
        self._audio_player.pause()
        self._play_button.visible = True
        self._pause_button.visible = False
        self.update()

    def stop(self) -> None:
        """停止音频"""
        self._audio_player.stop()
        self._play_button.visible = True
        self._pause_button.visible = False
        self._stop_button.visible = False
        self._progress_slider.value = 0
        self.update()

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
        self._audio_player.volume = volume

    def get_current_file(self) -> Optional[str]:
        """获取当前播放的文件"""
        return self._current_file

    def is_playing(self) -> bool:
        """检查是否正在播放"""
        return self._audio_player.get_state() == ft.AudioState.PLAYING
