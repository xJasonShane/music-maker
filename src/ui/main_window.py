"""
主窗口 - Flet主界面
"""
import flet as ft
import tkinter as tk
from typing import Dict, Any, Optional, List
from .audio_player import AudioPlayer
from .config_panel import ConfigPanel
from ..config.config_manager import config_manager
from ..ai.generator import GeneratorManager
from ..core.file_manager import FileManager
from ..core.history_manager import HistoryManager
from ..core.exceptions import MusicMakerException


class MusicMakerApp:
    """音悦应用主类"""

    def __init__(self):
        """
        初始化 MusicMaker 应用的状态、管理器和主要界面控件。
        
        加载并保存应用配置，创建生成器、文件管理和历史记录管理器；初始化界面可见性状态标志；并构建主要的输入与显示控件，包括提示词输入、多项下拉选择（模型、风格、节拍、时长）、生成按钮、结果文本区域、音频播放器和侧边导航栏。
        """
        self.page = None
        self.config = config_manager.load_config()
        self.generator_manager = GeneratorManager()
        self.generator_manager.create_from_config(self.config)
        self.file_manager = FileManager(self.config.get('app', {}).get('output_dir', './output'))
        self.history_manager = HistoryManager(self.config.get('app', {}).get('history_file', './history.json'))
        self._config_panel_visible = False
        self._history_panel_visible = False
        self._showing_history_detail = False

        self._paste_button = ft.IconButton(
            icon=ft.icons.Icons.CONTENT_PASTE,
            tooltip="粘贴",
            icon_color=ft.Colors.BLUE_600,
            on_click=self._on_paste_click
        )
        self._prompt_field = ft.TextField(
            label="提示词",
            hint_text="输入创作提示词，例如：创作一首关于春天的流行歌曲",
            multiline=True,
            min_lines=10,
            max_lines=14,
            expand=True,
            suffix=self._paste_button
        )
        self._model_dropdown = ft.Dropdown(
            label="AI模型",
            options=self._get_model_options(),
            value=self.config.get('current_model', 'openai'),
            width=200,
            border_radius=8,
            filled=True
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
            width=200,
            border_radius=8,
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
            border_radius=8,
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
            border_radius=8,
            filled=True
        )
        self._generate_button = ft.ElevatedButton(
            "生成",
            icon=ft.icons.Icons.AUTO_AWESOME,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12)
            ),
            expand=True,
            height=50
        )
        self._export_audio_button = ft.ElevatedButton(
            "导出歌曲",
            icon=ft.icons.Icons.AUDIO_FILE,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=15, vertical=10)
            ),
            expand=True
        )
        self._export_lyrics_button = ft.ElevatedButton(
            "导出歌词",
            icon=ft.icons.Icons.LYRICS,
            bgcolor=ft.Colors.ORANGE_600,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=15, vertical=10)
            ),
            expand=True
        )
        self._export_all_button = ft.ElevatedButton(
            "一键导出",
            icon=ft.icons.Icons.DOWNLOAD,
            bgcolor=ft.Colors.PURPLE_600,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=15, vertical=10)
            ),
            expand=True
        )
        self._result_text = ft.Text(
            "创作结果将在这里显示",
            selectable=True,
            expand=True
        )
        self._audio_player = AudioPlayer()

        self._nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=120,
            min_extended_width=200,
            bgcolor=ft.Colors.WHITE,
            selected_label_text_style=ft.TextStyle(
                size=14,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.BLUE_600
            ),
            unselected_label_text_style=ft.TextStyle(
                size=14,
                weight=ft.FontWeight.W_400,
                color=ft.Colors.GREY_700
            ),
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

    def _center_window(self, window_width: int, window_height: int) -> tuple:
        """
        计算并返回使窗口在当前屏幕居中的左上角坐标（支持多显示器）。
        
        Parameters:
            window_width (int): 窗口宽度（像素）。
            window_height (int): 窗口高度（像素）。
        
        Returns:
            tuple: (x, y) 窗口左上角坐标（像素）。若无法获取屏幕尺寸则返回默认坐标 (100, 100)。
        """
        try:
            root = tk.Tk()
            root.withdraw()
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            root.destroy()
            
            return x, y
        except Exception:
            return 100, 100

    def build(self, page: ft.Page) -> None:
        """
        构建并初始化应用主界面、各功能面板与交互回调。
        
        初始化页面主题与外观，创建并布局创作区、预览区、配置面板与历史面板，生成历史项并将主要内容保存到实例属性（如 _main_content、_config_content、_history_content），并为生成按钮、提示词输入与模型下拉绑定相应的事件回调以响应用户交互。
        
        参数:
            page (ft.Page): Flet 页面对象，用于挂载与配置应用的界面和交互。
        """
        self.page = page
        page.title = "音悦"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 10
        page.fonts = {
            "Microsoft YaHei": "msyh.ttc",
            "SimHei": "simhei.ttf"
        }
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE_600,
                on_primary=ft.Colors.WHITE,
                surface=ft.Colors.GREY_50,
                on_surface=ft.Colors.GREY_900,
            )
        )

        page.appbar = ft.AppBar(
            title=ft.Text("音悦", size=20, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.icons.Icons.SETTINGS,
                    tooltip="配置",
                    icon_color=ft.Colors.WHITE,
                    on_click=self._on_config_click
                )
            ]
        )

        creation_area = ft.Container(
            content=ft.Column([
                ft.Text("创作区", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ft.Divider(height=1),
                self._prompt_field,
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            self._model_dropdown,
                            self._style_dropdown
                        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            self._tempo_dropdown,
                            self._duration_dropdown
                        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        self._generate_button
                    ], spacing=10),
                )
            ], spacing=15),
            padding=20,
            border=ft.border.all(2, ft.Colors.BLUE_200),
            border_radius=12,
            bgcolor=ft.Colors.WHITE
        )

        preview_area = ft.Container(
            content=ft.Column([
                ft.Text("预览区", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Column([
                        ft.Text("音频播放", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_700),
                        self._audio_player.build(page)
                    ], spacing=3),
                    padding=8,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.GREY_50
                ),
                ft.Row([
                    self._export_audio_button,
                    self._export_lyrics_button,
                    self._export_all_button
                ], spacing=10, expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Text("歌词预览", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_700),
                        ft.Container(
                            content=ft.Column([
                                self._result_text
                            ], scroll=ft.ScrollMode.AUTO),
                            expand=True,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=8,
                            padding=10,
                            bgcolor=ft.Colors.WHITE
                        )
                    ], spacing=3),
                    expand=True,
                    padding=8,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.GREY_50
                )
            ], spacing=10, expand=True),
            padding=20,
            border=ft.border.all(2, ft.Colors.BLUE_200),
            border_radius=12,
            bgcolor=ft.Colors.WHITE
        )

        config_panel = ConfigPanel(self.config, self._on_save_config)
        config_area = config_panel.build(page)

        main_content = ft.Row([
            ft.Container(
                content=creation_area,
                width=450,
                expand=False
            ),
            ft.VerticalDivider(width=2, color=ft.Colors.GREY_300),
            ft.Container(
                content=preview_area,
                expand=True
            )
        ], expand=True, spacing=10)

        config_content = ft.Column([
            ft.Row([
                ft.Text("配置管理", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.CLOSE,
                    icon_color=ft.Colors.GREY_700,
                    tooltip="关闭",
                    on_click=self._on_config_click
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            config_area
        ], expand=True, spacing=10)

        self._main_content = main_content

        self._config_content = config_content

        history_records = self.history_manager.get_all_records()
        history_items = self._create_history_items(history_records)
        
        history_content = ft.Column([
            ft.Row([
                ft.Text("历史记录", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.REFRESH,
                    tooltip="刷新",
                    icon_color=ft.Colors.BLUE_600,
                    on_click=self._on_refresh_history
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            ft.Column(history_items, scroll=ft.ScrollMode.AUTO, spacing=15, expand=True)
        ], expand=True, spacing=10)

        self._history_content = history_content

        self._update_main_content()

        self._generate_button.on_click = self._on_generate_click
        self._prompt_field.on_change = self._update_generate_button
        self._model_dropdown.on_change = self._on_model_change
        self._export_audio_button.on_click = self._on_export_audio_click
        self._export_lyrics_button.on_click = self._on_export_lyrics_click
        self._export_all_button.on_click = self._on_export_all_click

    def _update_main_content(self) -> None:
        """
        根据当前面板状态渲染主内容区域。

        根据 _config_panel_visible、_showing_history_detail 和 _history_panel_visible 的优先级选择要显示的面板（配置面板、历史详情、历史列表或主面板），清除页面并将导航栏、内容区添加到页面以更新界面显示。
        """
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
                    content
                ], expand=True)
            )

    def _on_generate_click(self, e) -> None:
        """
        处理“生成”按钮点击：校验提示词并使用当前风格请求生成歌词，成功时展示结果并保存到历史，失败时显示错误信息。
        
        Parameters:
            e: 触发事件对象（来自 Flet 的点击事件），仅用于事件上下文，函数内部不直接读取其属性。
        """
        prompt = self._prompt_field.value

        if not prompt or not prompt.strip():
            self._show_error("请输入提示词")
            return

        try:
            result = self.generator_manager.generate_lyrics(
                prompt,
                style=self._style_dropdown.value,
                language='中文'
            )

            if result.get('success'):
                self._result_text.value = result.get('data', '')
                self._save_to_history('lyrics', prompt, result)
            else:
                self._show_error("生成失败")

        except MusicMakerException as ex:
            self._show_error(str(ex))
        except Exception as ex:
            self._show_error(f"发生错误: {str(ex)}")

    def _on_config_click(self, e) -> None:
        """
        切换配置面板的可见性并刷新主界面。
        
        在切换或刷新过程中若发生异常，会将异常信息输出并在界面上显示错误提示。
        """
        try:
            self._config_panel_visible = not self._config_panel_visible
            self._update_main_content()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self._show_error(f"打开设置失败: {str(ex)}")

    def _on_save_config(self, new_config: Dict[str, Any]) -> None:
        """
        保存并应用新的应用配置。
        
        将配置持久化到配置存储，替换运行时配置，基于新配置重建生成器实例并刷新可用模型选项以同步 UI。
        
        Parameters:
            new_config (Dict[str, Any]): 要保存并应用的配置字典。
        """
        config_manager.save_config(new_config)
        self.config = new_config
        self.generator_manager.create_from_config(self.config)
        self._update_model_options()

    def _get_model_options(self) -> List[ft.dropdown.Option]:
        """
        生成当前配置中已启用模型的下拉选项列表。
        
        Returns:
            List[ft.dropdown.Option]: 包含每个已启用模型的下拉选项；每项的 key 为模型 id，text 为模型 name（若未配置则使用 id）。
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

    def _on_paste_click(self, e) -> None:
        """
        处理粘贴按钮点击事件，从剪贴板粘贴内容到提示词输入框。
        """
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
        except Exception:
            pass

    def _on_model_change(self, e) -> None:
        """
        处理模型下拉选择变更，将新的模型标识保存到运行时配置与持久化配置。
        
        会读取当前下拉控件的值并将其设置为应用的当前模型，从而更新运行时配置和持久化配置存储。
        """
        new_model = self._model_dropdown.value
        config_manager.set_current_model(new_model)
        self.config['current_model'] = new_model

    def _on_nav_change(self, e) -> None:
        """
        根据导航栏选择在“创作”和“历史”面板间切换并刷新主界面。
        
        Parameters:
            e: 事件对象，期望包含 `control.selected_index` 字段；`0` 表示切换到“创作”面板，`1` 表示切换到“历史”面板。
        """
        if e.control.selected_index == 0:
            self._showing_history_detail = False
            self._history_panel_visible = False
            self._config_panel_visible = False
            self._update_main_content()
        elif e.control.selected_index == 1:
            self._showing_history_detail = False
            self._history_panel_visible = True
            self._config_panel_visible = False
            self._update_main_content()

    def _update_generate_button(self) -> None:
        """
        更新“生成”按钮的可用状态。
        
        当提示输入框包含至少一个非空白字符时启用生成按钮，否则禁用它。
        """
        if self._prompt_field.value and self._prompt_field.value.strip():
            self._generate_button.disabled = False
        else:
            self._generate_button.disabled = True

    def _show_error(self, message: str) -> None:
        """
        在页面底部以红色 SnackBar 显示错误消息并刷新页面。
        
        Parameters:
            message (str): 要显示的错误文本。
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def _on_export_audio_click(self, e) -> None:
        """
        处理导出歌曲按钮点击事件。
        
        Parameters:
            e: 触发事件对象。
        """
        self._show_info("导出歌曲功能开发中...")

    def _on_export_lyrics_click(self, e) -> None:
        """
        处理导出歌词按钮点击事件。
        
        Parameters:
            e: 触发事件对象。
        """
        self._show_info("导出歌词功能开发中...")

    def _on_export_all_click(self, e) -> None:
        """
        处理一键导出按钮点击事件。
        
        Parameters:
            e: 触发事件对象。
        """
        self._show_info("一键导出功能开发中...")

    def _show_info(self, message: str) -> None:
        """
        在页面底部以蓝色 SnackBar 显示信息消息并刷新页面。
        
        Parameters:
            message (str): 要显示的信息文本。
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.BLUE_600
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def _save_to_history(self, result_type: str, prompt: str, result: Dict[str, Any]) -> None:
        """
        将一次创作结果保存为历史记录条目。
        
        记录包含字段：`type`（结果类型）、`prompt`（提示词）、`result`（生成结果）、`style`、`tempo` 和 `duration`（后面三项从当前 UI 选择读取）。该条目会被添加到 history_manager 的记录列表中。
        
        Parameters:
            result_type (str): 本次结果的类型标识（例如 "lyrics"、"audio" 等）。
            prompt (str): 用于生成的提示词文本。
            result (Dict[str, Any]): 生成结果的具体数据（任意结构，按记录需要存储）。
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
        生成历史记录的 UI 列表项。
        
        将给定的历史记录列表转换为对应的 ft.Container 列表；每项显示记录编号、类型（中文）、创建时间、截断后的提示文本和风格，并在点击时调用 _on_history_item_click 打开记录详情。若 records 为空或无有效项，则返回一个显示“暂无历史记录”的占位容器。
        
        Parameters:
            records (List[Dict[str, Any]]): 包含历史记录字段（如 'id', 'prompt', 'type', 'created_at', 'style'）的字典列表。
        
        Returns:
            List[ft.Container]: 对应的历史记录 UI 项列表，或包含单个占位项的列表（当没有记录时）。
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
                        ft.Container(
                            content=ft.Text(f"#{record_id}", weight=ft.FontWeight.BOLD, size=16),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            bgcolor=ft.Colors.BLUE_100,
                            border_radius=6
                        ),
                        ft.Container(
                            content=ft.Text(type_text, size=14, weight=ft.FontWeight.W_500),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            bgcolor=ft.Colors.GREEN_100,
                            border_radius=6
                        ),
                        ft.Container(expand=True),
                        ft.Text(created_at[:19] if created_at else '', size=12, color=ft.Colors.GREY_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(
                        content=ft.Text(
                            prompt[:120] + '...' if len(prompt) > 120 else prompt,
                            size=15,
                            color=ft.Colors.GREY_800,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        padding=ft.padding.symmetric(vertical=5)
                    ),
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"风格: {style}", size=13, color=ft.Colors.GREY_700),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=4
                        )
                    ])
                ], spacing=8),
                padding=20,
                border=ft.border.all(2, ft.Colors.BLUE_100),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                on_click=lambda e, rid=record_id: self._on_history_item_click(e, rid)
            )
            items.append(item)
        
        if not items:
            items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.HISTORY, size=64, color=ft.Colors.GREY_300),
                        ft.Text("暂无历史记录", size=18, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                        ft.Text("开始创作后，您的作品将显示在这里", size=14, color=ft.Colors.GREY_400)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    border=ft.border.all(2, ft.Colors.GREY_200),
                    border_radius=12,
                    bgcolor=ft.Colors.GREY_50
                )
            )
        
        return items

    def _on_refresh_history(self, e) -> None:
        """
        刷新历史记录面板并更新主界面显示。
        
        构建新的历史项并替换当前历史内容后触发界面刷新。
        
        Parameters:
            e: 触发事件的对象，方法内部未使用，可为 None。
        """
        history_records = self.history_manager.get_all_records()
        history_items = self._create_history_items(history_records)
        
        history_content = ft.Column([
            ft.Row([
                ft.Text("历史记录", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.Icons.REFRESH,
                    tooltip="刷新",
                    icon_color=ft.Colors.BLUE_600,
                    on_click=self._on_refresh_history
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            ft.Column(history_items, scroll=ft.ScrollMode.AUTO, spacing=15, expand=True)
        ], expand=True, spacing=10)
        
        self._history_content = history_content
        
        self._update_main_content()

    def _on_history_item_click(self, e, record_id: int) -> None:
        """
        响应历史记录项被点击，查找对应记录并显示其详细视图；若记录不存在则显示错误信息。
        
        Parameters:
            e: 事件对象，表示点击事件（通常由 UI 传入）。
            record_id (int): 要打开的历史记录的唯一标识符。
        """
        record = self.history_manager.get_record_by_id(record_id)
        if not record:
            self._show_error(f"未找到记录 #{record_id}")
            return
        
        self._show_history_detail(record)

    def _show_history_detail(self, record: Dict[str, Any]) -> None:
        """
        显示单条历史记录的详细视图并将其渲染到主界面。
        
        Parameters:
            record (Dict[str, Any]): 包含历史记录字段的字典。常用字段：
                - id: 记录编号
                - prompt: 用于创作的提示词
                - result: 结果对象，通常包含 `data` 字段（创作内容）
                - type: 创作类型（如 'lyrics'、'melody'、'arrangement'）
                - created_at: 创建时间字符串
                - style: 风格描述
                - tempo: 节拍（BPM）
                - duration: 时长（秒）
        
        Side effects:
            - 构建并设置 self._history_detail_content 用于显示详情。
            - 将 self._showing_history_detail 置为 True。
            - 调用 self._update_main_content() 重新渲染主界面。
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
                    icon_color=ft.Colors.BLUE_600,
                    on_click=self._on_back_to_history
                ),
                ft.Text(f"历史记录详情 #{record_id}", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ft.Container(expand=True)
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            ft.Container(
                content=ft.Column([
                    ft.Text("创作信息", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("类型", size=14, color=ft.Colors.GREY_600),
                            width=80
                        ),
                        ft.Container(
                            content=ft.Text(type_text, size=14, weight=ft.FontWeight.W_500),
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            bgcolor=ft.Colors.GREEN_100,
                            border_radius=6
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("风格", size=14, color=ft.Colors.GREY_600),
                            width=80
                        ),
                        ft.Text(style, size=14, weight=ft.FontWeight.W_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("节拍", size=14, color=ft.Colors.GREY_600),
                            width=80
                        ),
                        ft.Text(f"{tempo} BPM", size=14, weight=ft.FontWeight.W_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("时长", size=14, color=ft.Colors.GREY_600),
                            width=80
                        ),
                        ft.Text(f"{duration} 秒", size=14, weight=ft.FontWeight.W_500)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("创建时间", size=14, color=ft.Colors.GREY_600),
                            width=80
                        ),
                        ft.Text(created_at[:19] if created_at else '', size=14, color=ft.Colors.GREY_700)
                    ], alignment=ft.MainAxisAlignment.START)
                ], spacing=10),
                padding=20,
                border=ft.border.all(2, ft.Colors.BLUE_200),
                border_radius=12,
                bgcolor=ft.Colors.WHITE
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("提示词", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Divider(height=1),
                    ft.Text(prompt, selectable=True, size=15, color=ft.Colors.GREY_700)
                ], spacing=10),
                padding=20,
                border=ft.border.all(2, ft.Colors.BLUE_200),
                border_radius=12,
                bgcolor=ft.Colors.WHITE
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("创作结果", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(result_data, selectable=True, size=15, color=ft.Colors.GREY_700)
                        ], scroll=ft.ScrollMode.AUTO),
                        height=400,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=15,
                        bgcolor=ft.Colors.GREY_50
                    )
                ], spacing=10),
                padding=20,
                border=ft.border.all(2, ft.Colors.BLUE_200),
                border_radius=12,
                bgcolor=ft.Colors.WHITE
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self._history_detail_content = detail_content
        
        self._showing_history_detail = True
        self._update_main_content()

    def _on_back_to_history(self, e) -> None:
        """
        切换回历史记录列表视图并刷新主界面。
        
        Parameters:
            e: 触发操作的事件对象，未使用但保留以兼容回调签名。
        """
        self._showing_history_detail = False
        self._history_panel_visible = True
        self._update_main_content()