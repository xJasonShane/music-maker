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
        self._config_panel_visible = False
        self._history_panel_visible = False
        self._showing_history_detail = False

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

        self._nav_rail = ft.NavigationRail(
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

        config_panel = ConfigPanel(self.config, self._on_save_config)
        config_area = config_panel.build(page)

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

        config_content = ft.Column([
            ft.Row([
                ft.Text("配置管理", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.CLOSE,
                    on_click=self._on_config_click
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            config_area
        ], expand=True)

        self._main_content = ft.Column([
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

        self._config_content = ft.Column([
            config_content,
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

        history_records = self.history_manager.get_all_records()
        history_items = self._create_history_items(history_records)
        
        history_content = ft.Column([
            ft.Row([
                ft.Text("历史记录", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.REFRESH,
                    tooltip="刷新",
                    on_click=self._on_refresh_history
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Column(history_items, scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)
        ], expand=True)

        self._history_content = ft.Column([
            history_content,
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

        self._update_main_content()

        self._update_generate_button()

        self._model_dropdown.on_change = self._on_model_change

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
                    ft.VerticalDivider(width=1),
                    ft.Column([
                        content,
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
        try:
            self._config_panel_visible = not self._config_panel_visible
            self._update_main_content()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self._show_error(f"打开设置失败: {str(ex)}")

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
            self._showing_history_detail = False
            self._history_panel_visible = False
            self._config_panel_visible = False
            self._update_main_content()
            self._update_status("创作模式")
        elif e.control.selected_index == 1:
            self._showing_history_detail = False
            self._history_panel_visible = True
            self._config_panel_visible = False
            self._update_main_content()
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

    def _create_history_items(self, records: List[Dict[str, Any]]) -> List[ft.Container]:
        """
        创建历史记录列表项

        Args:
            records: 历史记录列表

        Returns:
            历史记录项列表
        """
        items = []
        for record in records:
            record_id = record.get('id', 0)
            prompt = record.get('prompt', '')
            result_type = record.get('type', 'lyrics')
            created_at = record.get('created_at', '')
            style = record.get('style', '流行')
            
            type_map = {
                'lyrics': '歌词',
                'melody': '旋律',
                'arrangement': '编曲'
            }
            type_text = type_map.get(result_type, result_type)
            
            item = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"#{record_id}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        ft.Text(f" | {type_text}", color=ft.Colors.GREY_600),
                        ft.Container(expand=True),
                        ft.Text(created_at[:19] if created_at else '', size=12, color=ft.Colors.GREY_500)
                    ]),
                    ft.Text(
                        prompt[:100] + '...' if len(prompt) > 100 else prompt,
                        size=14,
                        color=ft.Colors.GREY_800
                    ),
                    ft.Row([
                        ft.Text(f"风格: {style}", size=12, color=ft.Colors.GREY_600)
                    ])
                ], spacing=5),
                padding=15,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                bgcolor=ft.Colors.WHITE,
                on_click=lambda e, rid=record_id: self._on_history_item_click(e, rid)
            )
            items.append(item)
        
        if not items:
            items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("暂无历史记录", color=ft.Colors.GREY_500)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=30
                )
            )
        
        return items

    def _on_refresh_history(self, e) -> None:
        """
        刷新历史记录

        Args:
            e: 事件对象
        """
        self._update_status("正在刷新历史记录...")
        history_records = self.history_manager.get_all_records()
        history_items = self._create_history_items(history_records)
        
        history_content = ft.Column([
            ft.Row([
                ft.Text("历史记录", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.REFRESH,
                    tooltip="刷新",
                    on_click=self._on_refresh_history
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Column(history_items, scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)
        ], expand=True)
        
        self._history_content = ft.Column([
            history_content,
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
        
        self._update_main_content()
        self._update_status("历史记录已刷新")

    def _on_history_item_click(self, e, record_id: int) -> None:
        """
        点击历史记录项事件

        Args:
            e: 事件对象
            record_id: 记录ID
        """
        record = self.history_manager.get_record_by_id(record_id)
        if not record:
            self._show_error(f"未找到记录 #{record_id}")
            return
        
        self._show_history_detail(record)

    def _show_history_detail(self, record: Dict[str, Any]) -> None:
        """
        显示历史记录详情

        Args:
            record: 历史记录
        """
        record_id = record.get('id', 0)
        prompt = record.get('prompt', '')
        result = record.get('result', {})
        result_type = record.get('type', 'lyrics')
        created_at = record.get('created_at', '')
        style = record.get('style', '流行')
        tempo = record.get('tempo', '120')
        duration = record.get('duration', '30')
        
        type_map = {
            'lyrics': '歌词',
            'melody': '旋律',
            'arrangement': '编曲'
        }
        type_text = type_map.get(result_type, result_type)
        
        result_data = result.get('data', '')
        
        detail_content = ft.Column([
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.Icons.ARROW_BACK,
                    tooltip="返回",
                    on_click=self._on_back_to_history
                ),
                ft.Text(f"历史记录详情 #{record_id}", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True)
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Text("创作信息", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text("类型: ", weight=ft.FontWeight.BOLD),
                        ft.Text(type_text)
                    ]),
                    ft.Row([
                        ft.Text("风格: ", weight=ft.FontWeight.BOLD),
                        ft.Text(style)
                    ]),
                    ft.Row([
                        ft.Text("节拍: ", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{tempo} BPM")
                    ]),
                    ft.Row([
                        ft.Text("时长: ", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{duration} 秒")
                    ]),
                    ft.Row([
                        ft.Text("创建时间: ", weight=ft.FontWeight.BOLD),
                        ft.Text(created_at[:19] if created_at else '')
                    ])
                ], spacing=8),
                padding=15,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                bgcolor=ft.Colors.WHITE
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("提示词", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(prompt, selectable=True)
                ], spacing=8),
                padding=15,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                bgcolor=ft.Colors.WHITE
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("创作结果", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(result_data, selectable=True)
                        ], scroll=ft.ScrollMode.AUTO),
                        height=300,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=10
                    )
                ], spacing=8),
                padding=15,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                bgcolor=ft.Colors.WHITE
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self._history_detail_content = ft.Column([
            detail_content,
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
        
        self._showing_history_detail = True
        self._update_main_content()
        self._update_status(f"查看历史记录 #{record_id}")

    def _on_back_to_history(self, e) -> None:
        """
        返回历史记录列表

        Args:
            e: 事件对象
        """
        self._showing_history_detail = False
        self._history_panel_visible = True
        self._update_main_content()
        self._update_status("历史记录")
