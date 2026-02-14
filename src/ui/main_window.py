"""
主窗口 - 重构版本
使用服务层架构，实现UI与业务逻辑分离
"""
import flet as ft
from typing import Dict, Any, Optional, List
import logging
import threading
from datetime import datetime
from pathlib import Path
from .audio_player import AudioPlayer
from .config_panel import ConfigPanel
from .theme import DesignSystem
from .components.loading_overlay import LoadingOverlay
from .components.history_card import HistoryCard
from ..config.config_manager import config_manager
from ..ai.generator import GeneratorManager
from ..core.file_manager import FileManager
from ..core.history_manager import HistoryManager
from ..core.exceptions import MusicMakerException
from ..services.message_service import MessageService, MessageType
from ..services.export_service import ExportService
from ..services.music_service import MusicService

logger = logging.getLogger(__name__)


class MusicMakerApp:
    """音悦应用主类 - 重构版本"""

    def __init__(self):
        """初始化应用"""
        self.page = None
        self.config = config_manager.load_config()
        
        self.generator_manager = GeneratorManager()
        self.generator_manager.create_from_config(self.config)
        
        self.file_manager = FileManager(self.config.get('app', {}).get('output_dir', './output'))
        self.history_manager = HistoryManager(self.config.get('app', {}).get('history_file', './history.json'))
        
        self._message_service = None
        self._export_service = ExportService(self.config.get('app', {}).get('output_dir', './output'))
        self._music_service = MusicService(self.generator_manager)
        
        self._config_panel_visible = False
        self._history_panel_visible = False
        self._showing_history_detail = False
        self._history_detail_content = None
        
        self._current_lyrics = None
        self._current_audio_path = None
        
        self._loading_overlay = LoadingOverlay("正在生成...")
        
        self._build_ui_components()

    def _build_ui_components(self) -> None:
        """构建所有UI组件"""
        self._loading_indicator = ft.ProgressRing(
            width=48,
            height=48,
            stroke_width=4,
            color=DesignSystem.Colors.PRIMARY,
            visible=False
        )
        
        self._loading_overlay = ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                ft.Column([
                    self._loading_indicator,
                    ft.Text("正在生成...", size=16, color=DesignSystem.Colors.TEXT_SECONDARY)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(expand=True)
            ], expand=True),
            bgcolor=ft.Colors.with_opacity(0.9, DesignSystem.Colors.WHITE),
            visible=False
        )

        self._paste_button = ft.IconButton(
            icon=ft.icons.Icons.CONTENT_PASTE,
            tooltip="粘贴",
            icon_color=DesignSystem.Colors.PRIMARY,
            on_click=self._on_paste_click
        )

        self._prompt_field = ft.TextField(
            label="描述您的创作灵感",
            hint_text="例如：创作一首关于夏天的轻快流行歌曲，充满阳光和活力",
            multiline=True,
            min_lines=8,
            max_lines=12,
            expand=True,
            suffix=self._paste_button,
            border_radius=DesignSystem.Radius.MD,
            filled=True
        )

        self._model_dropdown = ft.Dropdown(
            label="AI模型",
            options=self._get_model_options(),
            value=self.config.get('current_model', 'mock'),
            width=200,
            border_radius=DesignSystem.Radius.MD,
            filled=True
        )

        self._style_dropdown = ft.Dropdown(
            label="音乐风格",
            options=[
                ft.dropdown.Option("流行"),
                ft.dropdown.Option("摇滚"),
                ft.dropdown.Option("古典"),
                ft.dropdown.Option("电子"),
                ft.dropdown.Option("民谣"),
                ft.dropdown.Option("爵士")
            ],
            value="流行",
            width=200,
            border_radius=DesignSystem.Radius.MD,
            filled=True
        )

        self._tempo_dropdown = ft.Dropdown(
            label="节拍 (BPM)",
            options=[
                ft.dropdown.Option("60"),
                ft.dropdown.Option("90"),
                ft.dropdown.Option("120"),
                ft.dropdown.Option("140"),
                ft.dropdown.Option("180")
            ],
            value="120",
            width=200,
            border_radius=DesignSystem.Radius.MD,
            filled=True
        )

        self._duration_dropdown = ft.Dropdown(
            label="时长 (秒)",
            options=[
                ft.dropdown.Option("30"),
                ft.dropdown.Option("60"),
                ft.dropdown.Option("90"),
                ft.dropdown.Option("120")
            ],
            value="30",
            width=200,
            border_radius=DesignSystem.Radius.MD,
            filled=True
        )

        self._generate_button = ft.ElevatedButton(
            "开始创作",
            icon=ft.icons.Icons.AUTO_AWESOME,
            bgcolor=DesignSystem.Colors.PRIMARY,
            color=DesignSystem.Colors.WHITE,
            expand=True,
            height=56,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=DesignSystem.Radius.MD)
            ),
            on_click=self._on_generate_click
        )

        self._export_audio_button = ft.ElevatedButton(
            "导出歌曲",
            icon=ft.icons.Icons.AUDIO_FILE,
            bgcolor=DesignSystem.Colors.SUCCESS,
            color=DesignSystem.Colors.WHITE,
            expand=True,
            disabled=True,
            on_click=self._on_export_audio_click
        )

        self._export_lyrics_button = ft.ElevatedButton(
            "导出歌词",
            icon=ft.icons.Icons.LYRICS,
            bgcolor=DesignSystem.Colors.WARNING,
            color=DesignSystem.Colors.WHITE,
            expand=True,
            disabled=True,
            on_click=self._on_export_lyrics_click
        )

        self._export_all_button = ft.ElevatedButton(
            "一键导出",
            icon=ft.icons.Icons.DOWNLOAD,
            bgcolor=DesignSystem.Colors.PRIMARY_DARK,
            color=DesignSystem.Colors.WHITE,
            expand=True,
            disabled=True,
            on_click=self._on_export_all_click
        )

        self._result_text = ft.Text(
            "创作结果将在这里显示",
            selectable=True,
            expand=True,
            size=14,
            color=DesignSystem.Colors.TEXT_SECONDARY
        )

        self._audio_player = AudioPlayer()

        self._nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=180,
            bgcolor=DesignSystem.Colors.WHITE,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.Icons.CREATE,
                    selected_icon=ft.icons.Icons.CREATE,
                    label="创作"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.Icons.HISTORY,
                    selected_icon=ft.icons.Icons.HISTORY,
                    label="历史"
                )
            ],
            on_change=self._on_nav_change
        )

    def build(self, page: ft.Page) -> None:
        """构建主界面"""
        self.page = page
        self._message_service = MessageService(page)
        
        page.title = "音悦 - AI音乐创作"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = DesignSystem.Spacing.MD
        page.bgcolor = DesignSystem.Colors.BACKGROUND
        
        page.appbar = ft.AppBar(
            title=ft.Row([
                ft.Icon(ft.icons.Icons.MUSIC_NOTE, size=28, color=DesignSystem.Colors.WHITE),
                ft.Text(" 音悦", size=24, weight=ft.FontWeight.BOLD, color=DesignSystem.Colors.WHITE)
            ], spacing=4),
            bgcolor=DesignSystem.Colors.PRIMARY,
            color=DesignSystem.Colors.WHITE,
            elevation=2,
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.icons.Icons.SETTINGS,
                            tooltip="设置",
                            icon_color=DesignSystem.Colors.WHITE,
                            on_click=self._on_config_click
                        )
                    ], spacing=4),
                    padding=ft.padding.only(right=DesignSystem.Spacing.SM)
                )
            ]
        )

        creation_area = self._build_creation_area()
        preview_area = self._build_preview_area()
        config_panel = ConfigPanel(self.config, self._on_save_config, self._refresh_config_panel)
        
        main_content = ft.Row([
            ft.Container(
                content=creation_area,
                width=500,
                expand=False
            ),
            ft.VerticalDivider(width=1, color=DesignSystem.Colors.GREY_200),
            ft.Container(
                content=preview_area,
                expand=True
            )
        ], expand=True, spacing=DesignSystem.Spacing.LG)

        self._config_content = ft.Column([
            ft.Row([
                ft.Text("配置管理", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.CLOSE,
                    icon_color=DesignSystem.Colors.TEXT_SECONDARY,
                    tooltip="关闭",
                    on_click=self._on_config_click
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
            config_panel.build(page)
        ], expand=True, spacing=DesignSystem.Spacing.LG)

        history_records = self.history_manager.get_all_records()
        history_items = self._create_history_items(history_records)
        
        self._history_content = ft.Column([
            ft.Row([
                ft.Text("历史记录", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.REFRESH,
                    tooltip="刷新",
                    icon_color=DesignSystem.Colors.PRIMARY,
                    on_click=self._on_refresh_history
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
            ft.Column(history_items, scroll=ft.ScrollMode.AUTO, spacing=DesignSystem.Spacing.LG, expand=True)
        ], expand=True, spacing=DesignSystem.Spacing.LG)

        self._main_content = main_content
        self._update_main_content()
        
        self._prompt_field.on_change = self._update_generate_button
        self._model_dropdown.on_change = self._on_model_change

    def _build_creation_area(self) -> ft.Container:
        """构建创作区域"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("创作区", size=20, weight=ft.FontWeight.BOLD, color=DesignSystem.Colors.TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.icons.Icons.CREATE, size=20, color=DesignSystem.Colors.PRIMARY),
                        padding=DesignSystem.Spacing.SM,
                        bgcolor=DesignSystem.Colors.PRIMARY_LIGHT,
                        border_radius=DesignSystem.Radius.MD
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
                self._prompt_field,
                ft.Container(height=DesignSystem.Spacing.MD),
                ft.Column([
                    ft.Row([
                        self._model_dropdown,
                        self._style_dropdown
                    ], spacing=DesignSystem.Spacing.MD, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        self._tempo_dropdown,
                        self._duration_dropdown
                    ], spacing=DesignSystem.Spacing.MD, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=DesignSystem.Spacing.SM),
                    self._generate_button
                ], spacing=DesignSystem.Spacing.MD)
            ], spacing=0),
            padding=DesignSystem.Spacing.XL,
            border_radius=DesignSystem.Radius.LG,
            bgcolor=DesignSystem.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )

    def _build_preview_area(self) -> ft.Container:
        """构建预览区域"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("预览区", size=20, weight=ft.FontWeight.BOLD, color=DesignSystem.Colors.TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.icons.Icons.VISIBILITY, size=20, color=DesignSystem.Colors.SUCCESS),
                        padding=DesignSystem.Spacing.SM,
                        bgcolor=DesignSystem.Colors.SUCCESS_LIGHT,
                        border_radius=DesignSystem.Radius.MD
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
                ft.Container(
                    content=ft.Column([
                        ft.Text("音频播放", size=15, weight=ft.FontWeight.W_600, color=DesignSystem.Colors.TEXT_SECONDARY),
                        self._audio_player.build(self.page)
                    ], spacing=DesignSystem.Spacing.SM),
                    padding=DesignSystem.Spacing.LG,
                    border=ft.border.all(1, DesignSystem.Colors.GREY_300),
                    border_radius=DesignSystem.Radius.MD,
                    bgcolor=DesignSystem.Colors.GREY_50
                ),
                ft.Container(
                    content=ft.Row([
                        self._export_audio_button,
                        self._export_lyrics_button,
                        self._export_all_button
                    ], spacing=DesignSystem.Spacing.MD, expand=True),
                    padding=DesignSystem.Spacing.LG,
                    border=ft.border.all(1, DesignSystem.Colors.GREY_300),
                    border_radius=DesignSystem.Radius.MD,
                    bgcolor=DesignSystem.Colors.GREY_50
                ),
                ft.Column([
                    ft.Text("歌词预览", size=15, weight=ft.FontWeight.W_600, color=DesignSystem.Colors.TEXT_SECONDARY),
                    ft.Container(
                        content=ft.Column([
                            self._result_text
                        ], scroll=ft.ScrollMode.AUTO),
                        expand=True,
                        border=ft.border.all(1, DesignSystem.Colors.GREY_300),
                        border_radius=DesignSystem.Radius.MD,
                        padding=DesignSystem.Spacing.LG,
                        bgcolor=DesignSystem.Colors.WHITE
                    )
                ], spacing=DesignSystem.Spacing.SM, expand=True)
            ], spacing=DesignSystem.Spacing.LG, expand=True),
            padding=DesignSystem.Spacing.XL,
            border_radius=DesignSystem.Radius.LG,
            bgcolor=DesignSystem.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )

    def _update_main_content(self) -> None:
        """更新主内容区域"""
        if self.page:
            self.page.clean()
            
            if self._config_panel_visible:
                content = self._config_content
            elif self._showing_history_detail:
                content = self._history_detail_content
            elif self._history_panel_visible:
                content = self._history_content
            else:
                content = self._main_content
            
            self.page.add(
                ft.Row([
                    self._nav_rail,
                    ft.VerticalDivider(width=1, color=DesignSystem.Colors.GREY_200),
                    content
                ], expand=True)
            )

    def _validate_prompt(self, prompt: str) -> tuple[bool, str]:
        """验证提示词"""
        return self._music_service.validate_prompt(prompt)

    def _show_loading(self) -> None:
        """显示加载状态"""
        self._loading_overlay.show()
        if self._loading_overlay.component not in self.page.overlay:
            self.page.overlay.append(self._loading_overlay.component)
        self.page.update()

    def _hide_loading(self) -> None:
        """隐藏加载状态"""
        self._loading_overlay.hide()
        if self._loading_overlay.component in self.page.overlay:
            self.page.overlay.remove(self._loading_overlay.component)
        self.page.update()

    def _on_generate_click(self, e) -> None:
        """处理生成按钮点击"""
        prompt = self._prompt_field.value
        is_valid, error_msg = self._validate_prompt(prompt)
        if not is_valid:
            self._message_service.error(error_msg)
            return
        
        self._show_loading()
        
        def on_complete(result):
            self.page.invoke(lambda: self._on_generate_complete(result))
        
        def on_error(error):
            self.page.invoke(lambda: self._on_generate_error(error))
        
        self._music_service.generate_lyrics(
            prompt,
            style=self._style_dropdown.value,
            language='中文',
            on_complete=on_complete,
            on_error=on_error
        )

    def _on_generate_complete(self, result: Dict[str, Any]) -> None:
        """生成完成回调"""
        self._hide_loading()
        if result.get('success'):
            self._current_lyrics = result.get('data', '')
            self._result_text.value = self._current_lyrics
            self._result_text.color = DesignSystem.Colors.TEXT_PRIMARY
            self._save_to_history('lyrics', self._prompt_field.value, result)
            self._export_lyrics_button.disabled = False
            self._export_all_button.disabled = False
            logger.info("歌词生成成功")
            self._message_service.success("创作完成！")
            self.page.update()
        else:
            self._show_error("生成失败")

    def _on_generate_error(self, error: str) -> None:
        """生成错误回调"""
        self._hide_loading()
        self._message_service.error(error)

    def _on_config_click(self, e) -> None:
        """切换配置面板"""
        try:
            self._config_panel_visible = not self._config_panel_visible
            self._update_main_content()
            logger.info(f"配置面板可见性: {self._config_panel_visible}")
        except Exception as ex:
            logger.error(f"切换配置面板失败: {ex}", exc_info=True)
            self._message_service.error(f"打开设置失败: {str(ex)}")

    def _refresh_config_panel(self) -> None:
        """刷新配置面板"""
        try:
            config_panel = ConfigPanel(self.config, self._on_save_config, self._refresh_config_panel)
            self._config_content = ft.Column([
                ft.Row([
                    ft.Text("配置管理", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.Icons.CLOSE,
                        icon_color=DesignSystem.Colors.TEXT_SECONDARY,
                        tooltip="关闭",
                        on_click=self._on_config_click
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
                config_panel.build(self.page)
            ], expand=True, spacing=DesignSystem.Spacing.LG)
            self._update_main_content()
        except Exception as ex:
            logger.error(f"刷新配置面板失败: {ex}", exc_info=True)

    def _on_save_config(self, new_config: Dict[str, Any]) -> None:
        """保存配置"""
        try:
            config_manager.save_config(new_config)
            self.config = new_config
            self.generator_manager.create_from_config(self.config)
            self._update_model_options()
            self._refresh_config_panel()
            logger.info("配置已保存并应用")
            self._message_service.success("配置已保存")
        except Exception as ex:
            logger.error(f"保存配置失败: {ex}", exc_info=True)
            self._message_service.error(f"保存配置失败: {str(ex)}")

    def _get_model_options(self) -> List[ft.dropdown.Option]:
        """获取模型选项"""
        models_config = self.config.get('models', {})
        options = []
        
        available_generators = self.generator_manager.get_available_generators()
        
        if 'mock' in available_generators:
            options.append(ft.dropdown.Option(key='mock', text='演示模式 (无需API)'))

        for model_id, model_config in models_config.items():
            if model_config.get('enabled', False) and model_config.get('api_key'):
                model_name = model_config.get('name', model_id)
                options.append(ft.dropdown.Option(key=model_id, text=model_name))
        
        if not options and 'mock' in available_generators:
            options.append(ft.dropdown.Option(key='mock', text='演示模式 (无需API)'))
        
        return options

    def _update_model_options(self) -> None:
        """更新模型选项"""
        self._model_dropdown.options = self._get_model_options()
        current_model = self.config.get('current_model', 'mock')
        enabled_models = config_manager.get_enabled_models()

        if current_model not in enabled_models and enabled_models:
            self._model_dropdown.value = enabled_models[0]
            config_manager.set_current_model(enabled_models[0])
        elif current_model in enabled_models:
            self._model_dropdown.value = current_model

        if self.page:
            self.page.update()

    def _on_paste_click(self, e) -> None:
        """处理粘贴按钮点击"""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            clipboard_text = root.clipboard_get()
            root.destroy()
            
            if clipboard_text:
                current_text = self._prompt_field.value or ""
                if current_text:
                    self._prompt_field.value = current_text + "\n" + clipboard_text
                else:
                    self._prompt_field.value = clipboard_text
                self._update_generate_button()
                self.page.update()
                logger.info("已粘贴内容到提示词输入框")
        except Exception as ex:
            logger.warning(f"粘贴失败: {ex}")
            self._show_error("粘贴失败，请重试")

    def _on_model_change(self, e) -> None:
        """处理模型选择变更"""
        new_model = self._model_dropdown.value
        config_manager.set_current_model(new_model)
        self.config['current_model'] = new_model
        logger.info(f"模型已切换到: {new_model}")

    def _on_nav_change(self, e) -> None:
        """处理导航栏切换"""
        if e.control.selected_index == 0:
            self._showing_history_detail = False
            self._history_panel_visible = False
            self._config_panel_visible = False
            self._update_main_content()
            logger.info("切换到创作面板")
        elif e.control.selected_index == 1:
            self._showing_history_detail = False
            self._history_panel_visible = True
            self._config_panel_visible = False
            self._update_main_content()
            logger.info("切换到历史面板")

    def _update_generate_button(self) -> None:
        """更新生成按钮状态"""
        if self._prompt_field.value and self._prompt_field.value.strip():
            self._generate_button.disabled = False
        else:
            self._generate_button.disabled = True

    def _on_export_audio_click(self, e) -> None:
        """导出歌曲"""
        self._message_service.info("导出歌曲功能开发中...")

    def _on_export_lyrics_click(self, e) -> None:
        """导出歌词"""
        if not self._current_lyrics:
            self._message_service.error("没有可导出的歌词，请先生成歌词")
            return
        
        result = self._export_service.export_lyrics(self._current_lyrics)
        
        if result['success']:
            logger.info(f"歌词已导出到: {result['filepath']}")
            self._message_service.success(result['message'])
        else:
            logger.error(f"导出歌词失败: {result['message']}")
            self._message_service.error(result['message'])

    def _on_export_all_click(self, e) -> None:
        """一键导出"""
        if not self._current_lyrics:
            self._message_service.error("没有可导出的内容，请先生成")
            return
        
        result = self._export_service.export_all(lyrics=self._current_lyrics)
        
        if result['success']:
            logger.info(f"一键导出完成: {result['files']}")
            for msg in result['messages']:
                self._message_service.success(msg)
        else:
            for msg in result['messages']:
                self._message_service.error(msg)

    def _save_to_history(self, result_type: str, prompt: str, result: Dict[str, Any]) -> None:
        """保存到历史记录"""
        try:
            record = {
                'type': result_type,
                'prompt': prompt,
                'result': result,
                'style': self._style_dropdown.value,
                'tempo': self._tempo_dropdown.value,
                'duration': self._duration_dropdown.value
            }
            self.history_manager.add_record(record)
            logger.info(f"已保存历史记录: {result_type}")
        except Exception as ex:
            logger.error(f"保存历史记录失败: {ex}", exc_info=True)

    def _create_history_items(self, records: List[Dict[str, Any]]) -> List[ft.Container]:
        """创建历史记录项"""
        items = []
        for record in records:
            card = HistoryCard(record, on_click=self._on_history_item_click)
            items.append(card.component)
        
        if not items:
            items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.HISTORY, size=72, color=DesignSystem.Colors.GREY_300),
                        ft.Text("暂无历史记录", size=20, color=DesignSystem.Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                        ft.Text("开始创作后，您的作品将显示在这里", size=15, color=DesignSystem.Colors.TEXT_DISABLED)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=DesignSystem.Spacing.LG),
                    padding=DesignSystem.Spacing.XXXL,
                    border_radius=DesignSystem.Radius.LG,
                    bgcolor=DesignSystem.Colors.GREY_50
                )
            )
        
        return items

    def _on_refresh_history(self, e) -> None:
        """刷新历史记录"""
        try:
            history_records = self.history_manager.get_all_records()
            history_items = self._create_history_items(history_records)
            
            self._history_content = ft.Column([
                ft.Row([
                    ft.Text("历史记录", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.Icons.REFRESH,
                        tooltip="刷新",
                        icon_color=DesignSystem.Colors.PRIMARY,
                        on_click=self._on_refresh_history
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
                ft.Column(history_items, scroll=ft.ScrollMode.AUTO, spacing=DesignSystem.Spacing.LG, expand=True)
            ], expand=True, spacing=DesignSystem.Spacing.LG)
            
            self._update_main_content()
            logger.info("历史记录已刷新")
        except Exception as ex:
            logger.error(f"刷新历史记录失败: {ex}", exc_info=True)
            self._message_service.error(f"刷新失败: {str(ex)}")

    def _on_history_item_click(self, record_id: int) -> None:
        """打开历史记录详情"""
        try:
            record = self.history_manager.get_record_by_id(record_id)
            if not record:
                self._message_service.error(f"未找到记录 #{record_id}")
                return
            self._show_history_detail(record)
            logger.info(f"打开历史记录详情: #{record_id}")
        except Exception as ex:
            logger.error(f"打开历史记录详情失败: {ex}", exc_info=True)
            self._message_service.error(f"打开记录失败: {str(ex)}")

    def _show_history_detail(self, record: Dict[str, Any]) -> None:
        """显示历史记录详情"""
        record_id = record.get('id', 0)
        prompt = record.get('prompt', '')
        result = record.get('result', {})
        result_type = record.get('type', 'lyrics')
        created_at = record.get('created_at', '')
        style = record.get('style', '流行')
        tempo = record.get('tempo', '120')
        duration = record.get('duration', '30')
        
        type_map = {'lyrics': '歌词', 'melody': '旋律', 'arrangement': '编曲'}
        type_text = type_map.get(result_type, result_type)
        result_data = result.get('data', '')
        
        detail_content = ft.Column([
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.Icons.ARROW_BACK,
                    tooltip="返回",
                    icon_color=DesignSystem.Colors.PRIMARY,
                    on_click=self._on_back_to_history
                ),
                ft.Text(f"历史记录详情 #{record_id}", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True)
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=1, color=DesignSystem.Colors.GREY_200),
            ft.Container(
                content=ft.Column([
                    ft.Text("创作信息", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("类型", size=14, color=DesignSystem.Colors.TEXT_SECONDARY),
                            width=90
                        ),
                        ft.Container(
                            content=ft.Text(type_text, size=14, weight=ft.FontWeight.W_500),
                            padding=ft.padding.symmetric(horizontal=DesignSystem.Spacing.SM, vertical=DesignSystem.Spacing.XS),
                            bgcolor=DesignSystem.Colors.SUCCESS_LIGHT,
                            border_radius=DesignSystem.Radius.SM
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("风格", size=14, color=DesignSystem.Colors.TEXT_SECONDARY),
                            width=90
                        ),
                        ft.Text(style, size=14, weight=ft.FontWeight.W_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("节拍", size=14, color=DesignSystem.Colors.TEXT_SECONDARY),
                            width=90
                        ),
                        ft.Text(f"{tempo} BPM", size=14, weight=ft.FontWeight.W_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("时长", size=14, color=DesignSystem.Colors.TEXT_SECONDARY),
                            width=90
                        ),
                        ft.Text(f"{duration} 秒", size=14, weight=ft.FontWeight.W_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("创建时间", size=14, color=DesignSystem.Colors.TEXT_SECONDARY),
                            width=90
                        ),
                        ft.Text(created_at[:19] if created_at else '', size=14, color=DesignSystem.Colors.TEXT_SECONDARY)
                    ], alignment=ft.MainAxisAlignment.START)
                ], spacing=DesignSystem.Spacing.MD),
                padding=DesignSystem.Spacing.XL,
                border_radius=DesignSystem.Radius.LG,
                bgcolor=DesignSystem.Colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
                )
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("提示词", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    ft.Text(prompt, selectable=True, size=15, color=DesignSystem.Colors.TEXT_PRIMARY)
                ], spacing=DesignSystem.Spacing.MD),
                padding=DesignSystem.Spacing.XL,
                border_radius=DesignSystem.Radius.LG,
                bgcolor=DesignSystem.Colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
                )
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("创作结果", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(result_data, selectable=True, size=15, color=DesignSystem.Colors.TEXT_PRIMARY)
                        ], scroll=ft.ScrollMode.AUTO),
                        height=400,
                        border=ft.border.all(1, DesignSystem.Colors.GREY_300),
                        border_radius=DesignSystem.Radius.MD,
                        padding=DesignSystem.Spacing.LG,
                        bgcolor=DesignSystem.Colors.GREY_50
                    )
                ], spacing=DesignSystem.Spacing.MD),
                padding=DesignSystem.Spacing.XL,
                border_radius=DesignSystem.Radius.LG,
                bgcolor=DesignSystem.Colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
                )
            )
        ], spacing=DesignSystem.Spacing.LG, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self._history_detail_content = detail_content
        self._showing_history_detail = True
        self._update_main_content()

    def _on_back_to_history(self, e) -> None:
        """返回历史记录列表"""
        self._showing_history_detail = False
        self._history_panel_visible = True
        self._update_main_content()
        logger.info("返回历史记录列表")
