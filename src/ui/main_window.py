"""
主窗口 - Flet主界面
"""
import flet as ft
from typing import Dict, Any, Optional, List
from .audio_player import AudioPlayer
from .config_panel import ConfigPanel
from ..config.config_manager import config_manager
from ..ai.generator import GeneratorManager
from ..core.file_manager import FileManager
from ..core.history_manager import HistoryManager
from ..core.exceptions import MusicMakerException


class MusicMakerApp:
    """音乐创作应用主类"""

    def __init__(self):
        """初始化应用"""
        self.page = None
        self.config = config_manager.load_config()
        self.generator_manager = GeneratorManager()
        self.generator_manager.create_from_config(self.config)
        self.file_manager = FileManager(self.config.get('app', {}).get('output_dir', './output'))
        self.history_manager = HistoryManager(self.config.get('app', {}).get('history_file', './history.json'))

        self._prompt_field = ft.TextField(
            label="提示词",
            hint_text="输入创作提示词，例如：创作一首关于春天的流行歌曲",
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True
        )
        self._model_dropdown = ft.Dropdown(
            label="AI模型",
            options=self._get_model_options(),
            value=self.config.get('current_model', 'openai'),
            width=200
        )
        self._style_dropdown = ft.Dropdown(
            label="风格",
            options=[
                ft.dropdown.Option("流行"),
                ft.dropdown.Option("摇滚"),
                ft.dropdown.Option("古典"),
                ft.dropdown.Option("电子"),
                ft.dropdown.Option("民谣"),
                ft.dropdown.Option("爵士")
            ],
            value="流行",
            width=200
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
            width=150
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
            width=150
        )
        self._generate_button = ft.ElevatedButton(
            "生成",
            on_click=self._on_generate_click
        )
        self._result_text = ft.Text(
            "创作结果将在这里显示",
            selectable=True,
            expand=True
        )
        self._audio_player = AudioPlayer()
        self._status_bar = ft.Text("就绪", color=ft.Colors.GREY_600)
        self._progress_ring = ft.ProgressRing(visible=False)

    def build(self, page: ft.Page) -> None:
        """
        构建主界面

        Args:
            page: Flet页面
        """
        self.page = page
        page.title = "AI音乐创作软件"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.padding = 10

        page.appbar = ft.AppBar(
            title=ft.Text("AI音乐创作软件"),
            actions=[
                ft.IconButton(
                    icon=ft.icons.Icons.SETTINGS,
                    tooltip="配置",
                    on_click=self._on_config_click
                )
            ]
        )

        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
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

        creation_area = ft.Container(
            content=ft.Column([
                ft.Text("创作区", size=16, weight=ft.FontWeight.BOLD),
                self._prompt_field,
                ft.Row([
                    self._model_dropdown,
                    self._style_dropdown,
                    self._tempo_dropdown,
                    self._duration_dropdown,
                    self._generate_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE
        )

        preview_area = ft.Container(
            content=ft.Column([
                ft.Text("预览区", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        self._result_text
                    ], scroll=ft.ScrollMode.AUTO),
                    height=300,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=10
                ),
                self._audio_player.build(page)
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE
        )

        main_content = ft.Row([
            ft.Container(
                content=creation_area,
                width=400,
                expand=False
            ),
            ft.Container(
                content=preview_area,
                expand=True
            )
        ], expand=True)

        page.add(
            ft.Row([
                nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column([
                    main_content,
                    ft.Container(
                        content=ft.Row([
                            self._status_bar,
                            ft.Container(expand=True),
                            self._progress_ring
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=5,
                        bgcolor=ft.Colors.GREY_100
                    )
                ], expand=True)
            ], expand=True)
        )

        self._update_generate_button()

        self._model_dropdown.on_change = self._on_model_change

    def _on_generate_click(self, e) -> None:
        """生成按钮点击事件"""
        prompt = self._prompt_field.value

        if not prompt or not prompt.strip():
            self._show_error("请输入提示词")
            return

        self._show_loading(True)
        self._update_status("正在生成...")

        try:
            result = self.generator_manager.generate_lyrics(
                prompt,
                style=self._style_dropdown.value,
                language='中文'
            )

            if result.get('success'):
                self._result_text.value = result.get('data', '')
                self._save_to_history('lyrics', prompt, result)
                self._update_status("生成成功")
            else:
                self._show_error("生成失败")

        except MusicMakerException as ex:
            self._show_error(str(ex))
        except Exception as ex:
            self._show_error(f"发生错误: {str(ex)}")
        finally:
            self._show_loading(False)

    def _on_config_click(self, e) -> None:
        """配置按钮点击事件"""
        config_panel = ConfigPanel(self.config, self._on_save_config)
        dialog = ft.AlertDialog(
            title=ft.Text("配置管理"),
            content=config_panel.build(self.page),
            actions=[
                ft.TextButton("关闭", on_click=lambda _: self.page.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_save_config(self, new_config: Dict[str, Any]) -> None:
        """
        保存配置

        Args:
            new_config: 新配置
        """
        config_manager.save_config(new_config)
        self.config = new_config
        self.generator_manager.create_from_config(self.config)
        self._update_model_options()
        self._update_status("配置已保存")

    def _get_model_options(self) -> List[ft.dropdown.Option]:
        """
        获取模型选项

        Returns:
            模型选项列表
        """
        models_config = self.config.get('models', {})
        options = []

        for model_id, model_config in models_config.items():
            if model_config.get('enabled', False):
                model_name = model_config.get('name', model_id)
                options.append(ft.dropdown.Option(key=model_id, text=model_name))

        return options

    def _update_model_options(self) -> None:
        """更新模型选项"""
        self._model_dropdown.options = self._get_model_options()
        current_model = self.config.get('current_model', 'openai')
        enabled_models = config_manager.get_enabled_models()

        if current_model not in enabled_models and enabled_models:
            self._model_dropdown.value = enabled_models[0]
            config_manager.set_current_model(enabled_models[0])
        elif current_model in enabled_models:
            self._model_dropdown.value = current_model

        if self.page:
            self.page.update()

    def _on_model_change(self, e) -> None:
        """
        模型切换事件

        Args:
            e: 事件对象
        """
        new_model = self._model_dropdown.value
        config_manager.set_current_model(new_model)
        self.config['current_model'] = new_model
        self._update_status(f"已切换到 {new_model} 模型")

    def _on_nav_change(self, e) -> None:
        """导航栏切换事件"""
        if e.control.selected_index == 0:
            self._update_status("创作模式")
        elif e.control.selected_index == 1:
            self._update_status("历史记录")

    def _update_generate_button(self) -> None:
        """更新生成按钮状态"""
        if self._prompt_field.value and self._prompt_field.value.strip():
            self._generate_button.disabled = False
        else:
            self._generate_button.disabled = True

    def _show_loading(self, show: bool) -> None:
        """
        显示/隐藏加载状态

        Args:
            show: 是否显示
        """
        self._progress_ring.visible = show
        self._generate_button.disabled = show
        self.page.update()

    def _update_status(self, message: str) -> None:
        """
        更新状态栏

        Args:
            message: 状态消息
        """
        self._status_bar.value = message
        self.page.update()

    def _show_error(self, message: str) -> None:
        """
        显示错误消息

        Args:
            message: 错误消息
        """
        self._update_status(f"错误: {message}")
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def _save_to_history(self, result_type: str, prompt: str, result: Dict[str, Any]) -> None:
        """
        保存到历史记录

        Args:
            result_type: 结果类型
            prompt: 提示词
            result: 结果
        """
        record = {
            'type': result_type,
            'prompt': prompt,
            'result': result,
            'style': self._style_dropdown.value,
            'tempo': self._tempo_dropdown.value,
            'duration': self._duration_dropdown.value
        }
        self.history_manager.add_record(record)
