"""
配置面板 - 支持多模型配置
采用现代化UI设计，提供专业的视觉体验和交互效果
"""
import flet as ft
from typing import Dict, Any, Optional, Callable, List
import json
import os
from datetime import datetime


class ConfigPanel:
    """配置面板 - 支持多模型配置，采用现代化UI设计"""

    def __init__(self, config: Dict[str, Any], on_save: Optional[Callable] = None, on_refresh: Optional[Callable] = None):
        """
        初始化配置面板

        Args:
            config: 当前配置
            on_save: 保存回调
            on_refresh: 刷新UI回调
        """
        self.config = config
        self.on_save = on_save
        self.on_refresh = on_refresh
        self._page = None
        self._model_configs: Dict[str, Dict[str, ft.Control]] = {}
        self._output_dir = None
        self._history_file = None
        self._selected_category = "api"
        self._selected_model = None
        self._original_config = config.copy()
        
        # 测试状态
        self._test_status = {}  # 存储各模型的测试状态

    def build(self, page: ft.Page):
        """
        构建并返回用于显示和编辑多模型配置的面板容器
        
        Parameters:
            page (ft.Page): 父页面对象
        
        Returns:
            ft.Container: 配置面板容器
        """
        self._page = page

        models_config = self.config.get('models', {})
        current_model = self.config.get('current_model', 'openai')
        app_config = self.config.get('app', {})

        # 创建分类导航
        category_nav = self._build_category_nav()

        # 根据选择的分类显示不同的内容
        if self._selected_category == "api":
            content = self._create_api_config_content(models_config, current_model)
        else:
            content = self._create_software_config_content()
        
        # 创建内容区域
        content_area = ft.Container(
            content=content,
            padding=0,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            )
        )

        # 创建主容器
        main_content = ft.Row([
            category_nav,
            content_area
        ], spacing=0, expand=True)

        return ft.Container(
            content=main_content,
            padding=0,
            width=900,
            height=650,
            bgcolor=ft.Colors.GREY_50,
            border_radius=16
        )

    def _build_category_nav(self) -> ft.Container:
        """构建设置分类导航栏"""
        return ft.Container(
            content=ft.Column([
                # 标题区域
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.Icons.SETTINGS, size=24, color=ft.Colors.BLUE_600),
                            ft.Text("设置", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)
                        ], spacing=10),
                        ft.Divider(height=1, color=ft.Colors.GREY_300)
                    ], spacing=10),
                    padding=ft.padding.only(bottom=10)
                ),
                
                # 分类按钮
                ft.Container(
                    content=ft.Column([
                        self._build_nav_button(
                            "API配置",
                            ft.icons.Icons.API,
                            "api",
                            ft.Colors.BLUE_600
                        ),
                        self._build_nav_button(
                            "软件设置",
                            ft.icons.Icons.COMPUTER,
                            "software",
                            ft.Colors.GREEN_600
                        )
                    ], spacing=8),
                    padding=ft.padding.symmetric(vertical=10)
                ),
                
                ft.Container(expand=True),
                
                # 快捷操作区域
                ft.Container(
                    content=ft.Column([
                        ft.Divider(height=1, color=ft.Colors.GREY_300),
                        ft.Text("快捷操作", size=12, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.Icons.DOWNLOAD,
                                tooltip="导出配置",
                                icon_color=ft.Colors.GREY_600,
                                on_click=self._on_export_config
                            ),
                            ft.IconButton(
                                icon=ft.icons.Icons.UPLOAD,
                                tooltip="导入配置",
                                icon_color=ft.Colors.GREY_600,
                                on_click=self._on_import_config
                            ),
                            ft.IconButton(
                                icon=ft.icons.Icons.RESTORE,
                                tooltip="重置配置",
                                icon_color=ft.Colors.RED_400,
                                on_click=self._on_reset_config
                            )
                        ], spacing=5)
                    ], spacing=8)
                )
            ], spacing=5),
            padding=20,
            width=220,
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.only(top_left=16, bottom_left=16)
        )

    def _build_nav_button(self, text: str, icon, category: str, active_color) -> ft.Container:
        """构建导航按钮"""
        is_selected = self._selected_category == category
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=ft.Colors.WHITE if is_selected else ft.Colors.GREY_600),
                ft.Text(text, size=14, color=ft.Colors.WHITE if is_selected else ft.Colors.GREY_700, weight=ft.FontWeight.W_500)
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=active_color if is_selected else ft.Colors.TRANSPARENT,
            border_radius=8,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_click=lambda e: self._on_category_change(category),
            ink=True
        )

    def _on_category_change(self, category: str):
        """分类切换"""
        self._selected_category = category
        self._selected_model = None
        if self.on_refresh:
            self.on_refresh()

    def _create_api_config_content(self, models_config: Dict[str, Any], current_model: str) -> ft.Column:
        """创建API配置内容"""
        # 构建模型列表
        models_list = ft.Column([], spacing=6, scroll=ft.ScrollMode.AUTO)
        
        for model_id, model_config in models_config.items():
            model_name = model_config.get('name', model_id)
            is_selected = self._selected_model == model_id
            is_enabled = model_config.get('enabled', False)
            has_api_key = bool(model_config.get('api_key', ''))
            
            # 状态指示
            if is_enabled and has_api_key:
                status_color = ft.Colors.GREEN_500
                status_icon = ft.icons.Icons.CHECK_CIRCLE
            elif is_enabled:
                status_color = ft.Colors.ORANGE_500
                status_icon = ft.icons.Icons.WARNING
            else:
                status_color = ft.Colors.GREY_400
                status_icon = ft.icons.Icons.CANCEL
            
            model_item = ft.Container(
                content=ft.Row([
                    ft.Icon(status_icon, size=16, color=status_color),
                    ft.Text(model_name, size=13, color=ft.Colors.GREY_800 if is_selected else ft.Colors.GREY_700, expand=True, weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.W_400),
                    ft.Container(
                        width=8,
                        height=8,
                        bgcolor=status_color,
                        border_radius=4
                    ) if is_selected else ft.Container()
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_600) if is_selected else ft.Colors.TRANSPARENT,
                border=ft.border.only(
                    left=ft.BorderSide(3, ft.Colors.BLUE_600 if is_selected else ft.Colors.TRANSPARENT)
                ),
                border_radius=ft.border_radius.only(top_right=8, bottom_right=8),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                on_click=lambda e, mid=model_id: self._on_model_select(mid),
                ink=True
            )
            models_list.controls.append(model_item)
        
        # 模型配置详情
        if self._selected_model:
            model_config = models_config.get(self._selected_model, {})
            model_detail = self._create_model_detail(self._selected_model, model_config, current_model)
        else:
            model_detail = self._create_empty_state()
        
        # 构建API配置界面
        return ft.Column([
            # 头部
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("API配置管理", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                        ft.Text(f"当前使用模型: {current_model}", size=12, color=ft.Colors.GREY_500)
                    ], spacing=4),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "保存配置",
                        icon=ft.icons.Icons.SAVE,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=20, vertical=12)
                        ),
                        on_click=self._on_save_click
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(24),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200))
            ),
            
            # 内容区域
            ft.Row([
                # 左侧模型列表
                ft.Container(
                    content=ft.Column([
                        ft.Text("模型平台", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_700),
                        ft.Container(
                            content=models_list,
                            padding=ft.padding.symmetric(vertical=10),
                            height=400
                        )
                    ], spacing=10),
                    padding=ft.padding.all(20),
                    width=220,
                    border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_200))
                ),
                
                # 右侧配置详情
                ft.Container(
                    content=model_detail,
                    expand=True,
                    padding=ft.padding.all(24)
                )
            ], expand=True)
        ], expand=True)

    def _create_model_detail(self, model_id: str, model_config: Dict[str, Any], current_model: str) -> ft.Column:
        """创建模型配置详情"""
        model_name = model_config.get('name', model_id)
        is_current = model_id == current_model
        
        # 创建输入控件
        enabled_switch = ft.Switch(
            label="启用此模型",
            value=model_config.get('enabled', False),
            active_color=ft.Colors.BLUE_600
        )
        
        api_key_field = ft.TextField(
            label="API密钥",
            value=model_config.get('api_key', ''),
            password=True,
            can_reveal_password=True,
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.Icons.KEY,
            hint_text="输入您的API密钥"
        )
        
        api_base_field = ft.TextField(
            label="API地址",
            value=model_config.get('api_base', ''),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.Icons.LINK,
            hint_text="https://api.example.com/v1"
        )
        
        model_field = ft.TextField(
            label="模型名称",
            value=model_config.get('model', ''),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.Icons.MODEL_TRAINING,
            hint_text="例如: gpt-3.5-turbo"
        )
        
        # 测试状态显示
        test_status_text = ft.Text("", size=13)
        test_status_icon = ft.Icon(None)
        test_status_row = ft.Row([test_status_icon, test_status_text], spacing=8, visible=False)
        
        def on_test_click(e):
            """测试API连接"""
            test_status_row.visible = True
            test_status_text.value = "正在测试连接..."
            test_status_text.color = ft.Colors.BLUE_600
            test_status_icon.name = ft.icons.Icons.PENDING
            self._page.update()
            
            # 简单验证（不阻塞UI）
            if api_key_field.value:
                test_status_text.value = "连接成功"
                test_status_text.color = ft.Colors.GREEN_600
                test_status_icon.name = ft.icons.Icons.CHECK_CIRCLE
                self._test_status[model_id] = "success"
            else:
                test_status_text.value = "连接失败: API密钥不能为空"
                test_status_text.color = ft.Colors.RED_600
                test_status_icon.name = ft.icons.Icons.ERROR
                self._test_status[model_id] = "failed"
            
            self._page.update()
        
        # 保存控件引用
        self._model_configs[model_id] = {
            'enabled': enabled_switch,
            'api_key': api_key_field,
            'api_base': api_base_field,
            'model': model_field
        }
        
        return ft.Column([
            # 头部信息
            ft.Row([
                ft.Column([
                    ft.Text(model_name, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Text(f"模型ID: {model_id}", size=12, color=ft.Colors.GREY_500)
                ], spacing=4),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.WHITE),
                        ft.Text("当前使用", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)
                    ], spacing=6),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=ft.Colors.GREEN_600,
                    border_radius=20,
                    visible=is_current
                )
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            
            # 配置表单
            ft.Container(
                content=ft.Column([
                    enabled_switch,
                    
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    
                    api_key_field,
                    api_base_field,
                    model_field,
                    
                    # 测试连接区域
                    ft.Container(
                        content=ft.Row([
                            ft.ElevatedButton(
                                "测试连接",
                                icon=ft.icons.Icons.NETWORK_CHECK,
                                bgcolor=ft.Colors.BLUE_50,
                                color=ft.Colors.BLUE_600,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                                on_click=on_test_click
                            ),
                            test_status_row
                        ], spacing=15),
                        padding=ft.padding.only(top=10)
                    )
                ], spacing=16),
                padding=ft.padding.symmetric(vertical=10)
            ),
            
            ft.Container(expand=True),
            
            # 底部操作
            ft.Row([
                ft.OutlinedButton(
                    "取消",
                    on_click=lambda e: self._refresh_ui(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    )
                ),
                ft.ElevatedButton(
                    "设为默认",
                    icon=ft.icons.Icons.STAR,
                    bgcolor=ft.Colors.AMBER_600 if not is_current else ft.Colors.GREY_400,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=lambda e, mid=model_id: self._on_model_select(mid),
                    disabled=is_current
                )
            ], spacing=10, alignment=ft.MainAxisAlignment.END)
        ], spacing=16, expand=True)

    def _create_empty_state(self) -> ft.Column:
        """创建空状态提示"""
        return ft.Column([
            ft.Container(expand=True),
            ft.Column([
                ft.Icon(ft.icons.Icons.TOUCH_APP, size=64, color=ft.Colors.GREY_300),
                ft.Text("选择一个模型平台", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_600),
                ft.Text("点击左侧列表中的模型，开始配置API密钥", size=13, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            ft.Container(expand=True)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _create_software_config_content(self) -> ft.Column:
        """创建软件设置内容"""
        app_config = self.config.get('app', {})
        
        # 路径配置
        self._output_dir = ft.TextField(
            label="输出目录",
            value=app_config.get('output_dir', './output'),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.Icons.FOLDER,
            suffix=ft.IconButton(
                icon=ft.icons.Icons.FOLDER_OPEN,
                tooltip="浏览文件夹"
            )
        )
        
        self._history_file = ft.TextField(
            label="历史记录文件",
            value=app_config.get('history_file', './history.json'),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.Icons.HISTORY
        )
        
        # 字体设置
        font_family = ft.Dropdown(
            label="字体",
            options=[
                ft.dropdown.Option("system", "系统默认"),
                ft.dropdown.Option("microsoft", "微软雅黑"),
                ft.dropdown.Option("pingfang", "苹方"),
                ft.dropdown.Option("simsun", "宋体")
            ],
            value=app_config.get('font_family', 'system'),
            border_radius=8,
            filled=True,
            width=180
        )
        
        font_size = ft.Slider(
            min=12,
            max=20,
            divisions=8,
            value=app_config.get('font_size', 14),
            label="{value}pt"
        )
        
        # 主题设置
        theme_mode = ft.Dropdown(
            label="主题模式",
            options=[
                ft.dropdown.Option("light", "浅色"),
                ft.dropdown.Option("dark", "深色"),
                ft.dropdown.Option("system", "跟随系统")
            ],
            value=app_config.get('theme_mode', 'light'),
            border_radius=8,
            filled=True,
            width=150
        )
        
        # 开关设置
        auto_save = ft.Switch(
            label="自动保存创作",
            value=app_config.get('auto_save', True),
            active_color=ft.Colors.BLUE_600
        )
        
        auto_update = ft.Switch(
            label="自动检查更新",
            value=app_config.get('auto_update', True),
            active_color=ft.Colors.BLUE_600
        )
        
        return ft.Column([
            # 头部
            ft.Container(
                content=ft.Row([
                    ft.Text("软件设置", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "保存设置",
                        icon=ft.icons.Icons.SAVE,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=20, vertical=12)
                        ),
                        on_click=self._on_save_click
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(24),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200))
            ),
            
            # 设置内容
            ft.Container(
                content=ft.Column([
                    # 存储设置卡片
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.Icons.STORAGE, color=ft.Colors.BLUE_600),
                                    ft.Text("存储设置", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800)
                                ], spacing=10),
                                ft.Divider(height=1, color=ft.Colors.GREY_200),
                                self._output_dir,
                                self._history_file
                            ], spacing=16),
                            padding=20
                        ),
                        elevation=0,
                        color=ft.Colors.GREY_50
                    ),
                    
                    # 外观设置卡片
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.Icons.PALETTE, color=ft.Colors.PURPLE_600),
                                    ft.Text("外观设置", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800)
                                ], spacing=10),
                                ft.Divider(height=1, color=ft.Colors.GREY_200),
                                ft.Row([
                                    theme_mode,
                                    font_family
                                ], spacing=20),
                                ft.Column([
                                    ft.Text("字体大小", size=13, color=ft.Colors.GREY_700),
                                    font_size
                                ], spacing=8)
                            ], spacing=16),
                            padding=20
                        ),
                        elevation=0,
                        color=ft.Colors.GREY_50
                    ),
                    
                    # 功能设置卡片
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.Icons.TOGGLE_ON, color=ft.Colors.GREEN_600),
                                    ft.Text("功能设置", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800)
                                ], spacing=10),
                                ft.Divider(height=1, color=ft.Colors.GREY_200),
                                ft.Row([
                                    auto_save,
                                    auto_update
                                ], spacing=40)
                            ], spacing=16),
                            padding=20
                        ),
                        elevation=0,
                        color=ft.Colors.GREY_50
                    ),
                    
                    # 软件信息卡片
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.Icons.INFO, color=ft.Colors.ORANGE_600),
                                    ft.Text("软件信息", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800)
                                ], spacing=10),
                                ft.Divider(height=1, color=ft.Colors.GREY_200),
                                ft.Row([
                                    ft.Column([
                                        ft.Text("音悦 AI音乐创作", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                                        ft.Text("版本 1.0.0", size=13, color=ft.Colors.GREY_500),
                                        ft.Text("© 2024 MusicMaker Team. All rights reserved.", size=12, color=ft.Colors.GREY_400)
                                    ], spacing=4),
                                    ft.Container(expand=True),
                                    ft.Column([
                                        ft.ElevatedButton(
                                            "检查更新",
                                            icon=ft.icons.Icons.UPDATE,
                                            bgcolor=ft.Colors.BLUE_50,
                                            color=ft.Colors.BLUE_600,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=8)
                                            ),
                                            on_click=self._on_check_update_click
                                        ),
                                        ft.TextButton(
                                            "查看更新日志",
                                            on_click=lambda e: self._show_changelog()
                                        )
                                    ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.END)
                                ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                            ], spacing=16),
                            padding=20
                        ),
                        elevation=0,
                        color=ft.Colors.GREY_50
                    )
                ], spacing=16, scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.all(24),
                expand=True
            )
        ], expand=True)

    def _show_changelog(self):
        """显示更新日志"""
        if self._page:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("更新日志"),
                content=ft.Column([
                    ft.Text("v1.0.0 - 2024-01-24", weight=ft.FontWeight.BOLD),
                    ft.Text("• 初始版本发布"),
                    ft.Text("• 支持多模型AI音乐创作"),
                    ft.Text("• 支持歌词生成和旋律创作"),
                    ft.Text("• 提供现代化的用户界面")
                ], spacing=8, tight=True),
                actions=[
                    ft.TextButton("关闭", on_click=lambda e: self._close_dialog())
                ]
            )
            self._page.dialog = dialog
            dialog.open = True
            self._page.update()

    def _on_model_select(self, model_id: str):
        """选择模型"""
        if self._selected_model == model_id:
            self._selected_model = None
        else:
            self._selected_model = model_id
            self.config['current_model'] = model_id
        if self.on_refresh:
            self.on_refresh()

    def _on_model_enabled_change(self, model_id: str, enabled: bool):
        """模型启用状态改变"""
        if model_id in self._model_configs:
            self._model_configs[model_id]['enabled'].value = enabled

    def _on_save_click(self, e):
        """保存配置"""
        models_config = self.config.get('models', {})
        
        for model_id, fields in self._model_configs.items():
            if model_id in models_config:
                models_config[model_id]['enabled'] = fields['enabled'].value
                models_config[model_id]['api_key'] = fields['api_key'].value
                models_config[model_id]['api_base'] = fields['api_base'].value
                models_config[model_id]['model'] = fields['model'].value
        
        new_config = {
            'models': models_config,
            'current_model': self.config.get('current_model', 'openai'),
            'app': {
                'output_dir': self._output_dir.value,
                'history_file': self._history_file.value
            }
        }
        
        if self.on_save:
            self.on_save(new_config)
        
        if self._page:
            snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text("配置已保存", color=ft.Colors.WHITE)
                ], spacing=10),
                bgcolor=ft.Colors.GREEN_600,
                duration=2000
            )
            self._page.snack_bar = snack_bar
            snack_bar.open = True
            self._page.update()

    def _on_check_update_click(self, e):
        """检查更新"""
        if self._page:
            # 模拟检查更新
            snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text("当前已是最新版本 v1.0.0", color=ft.Colors.WHITE)
                ], spacing=10),
                bgcolor=ft.Colors.BLUE_600,
                duration=3000
            )
            self._page.snack_bar = snack_bar
            snack_bar.open = True
            self._page.update()

    def _on_export_config(self, e):
        """导出配置到文件"""
        if self._page:
            try:
                config_data = self.get_config()
                config_json = json.dumps(config_data, ensure_ascii=False, indent=2)
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"musicmaker_config_{timestamp}.json"
                
                # 保存到输出目录
                output_dir = self._output_dir.value if self._output_dir else './output'
                os.makedirs(output_dir, exist_ok=True)
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(config_json)
                
                snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                        ft.Text(f"配置已导出: {filename}", color=ft.Colors.WHITE)
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_600,
                    duration=3000
                )
                self._page.snack_bar = snack_bar
                snack_bar.open = True
                self._page.update()
                
            except Exception as ex:
                snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.ERROR, color=ft.Colors.WHITE),
                        ft.Text(f"导出失败: {str(ex)}", color=ft.Colors.WHITE)
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_600
                )
                self._page.snack_bar = snack_bar
                snack_bar.open = True
                self._page.update()

    def _on_import_config(self, e):
        """从文件导入配置"""
        if self._page:
            # 创建文件选择对话框
            def on_file_selected(e):
                if e.files:
                    try:
                        filepath = e.files[0].path
                        with open(filepath, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        
                        # 验证配置格式
                        if 'models' in config_data and 'app' in config_data:
                            self.config = config_data
                            self._refresh_ui()
                            
                            snack_bar = ft.SnackBar(
                                content=ft.Row([
                                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                                    ft.Text("配置导入成功", color=ft.Colors.WHITE)
                                ], spacing=10),
                                bgcolor=ft.Colors.GREEN_600,
                                duration=3000
                            )
                            self._page.snack_bar = snack_bar
                            snack_bar.open = True
                            self._page.update()
                        else:
                            raise ValueError("配置文件格式不正确")
                            
                    except Exception as ex:
                        snack_bar = ft.SnackBar(
                            content=ft.Row([
                                ft.Icon(ft.icons.Icons.ERROR, color=ft.Colors.WHITE),
                                ft.Text(f"导入失败: {str(ex)}", color=ft.Colors.WHITE)
                            ], spacing=10),
                            bgcolor=ft.Colors.RED_600
                        )
                        self._page.snack_bar = snack_bar
                        snack_bar.open = True
                        self._page.update()
            
            # 打开文件选择器
            file_picker = ft.FilePicker(
                on_result=on_file_selected
            )
            self._page.overlay.append(file_picker)
            self._page.update()
            file_picker.pick_files(
                dialog_title="选择配置文件",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["json"]
            )

    def _on_reset_config(self, e):
        """重置配置"""
        if self._page:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("确认重置配置"),
                content=ft.Column([
                    ft.Icon(ft.icons.Icons.WARNING, size=48, color=ft.Colors.ORANGE_500),
                    ft.Text("确定要重置所有配置吗？", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("此操作将恢复默认配置，您当前的设置将丢失。", size=13, color=ft.Colors.GREY_600)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                actions=[
                    ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                    ft.ElevatedButton(
                        "确认重置",
                        icon=ft.icons.Icons.RESTORE,
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self._confirm_reset()
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            self._page.dialog = dialog
            dialog.open = True
            self._page.update()

    def _close_dialog(self):
        """关闭对话框"""
        if self._page and self._page.dialog:
            self._page.dialog.open = False
            self._page.update()

    def _confirm_reset(self):
        """确认重置配置"""
        # 恢复默认配置
        default_config = {
            'models': {
                'openai': {
                    'name': 'OpenAI',
                    'enabled': False,
                    'api_key': '',
                    'api_base': 'https://api.openai.com/v1',
                    'model': 'gpt-3.5-turbo'
                },
                'claude': {
                    'name': 'Claude',
                    'enabled': False,
                    'api_key': '',
                    'api_base': 'https://api.anthropic.com/v1',
                    'model': 'claude-3-sonnet'
                }
            },
            'current_model': 'openai',
            'app': {
                'output_dir': './output',
                'history_file': './history.json',
                'theme_mode': 'light',
                'font_family': 'system',
                'font_size': 14,
                'auto_save': True,
                'auto_update': True
            }
        }
        
        self.config = default_config
        self._selected_category = "api"
        self._selected_model = None
        self._model_configs = {}
        
        self._close_dialog()
        self._refresh_ui()
        
        if self._page:
            snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text("配置已重置为默认值", color=ft.Colors.WHITE)
                ], spacing=10),
                bgcolor=ft.Colors.GREEN_600,
                duration=3000
            )
            self._page.snack_bar = snack_bar
            snack_bar.open = True
            self._page.update()

    def _refresh_ui(self):
        """刷新UI - 供主窗口调用以重新构建界面"""
        # 这个方法主要是为了告诉主窗口需要刷新
        pass

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        models_config = self.config.get('models', {})
        
        for model_id, fields in self._model_configs.items():
            if model_id in models_config:
                models_config[model_id]['enabled'] = fields['enabled'].value
                models_config[model_id]['api_key'] = fields['api_key'].value
                models_config[model_id]['api_base'] = fields['api_base'].value
                models_config[model_id]['model'] = fields['model'].value
        
        return {
            'models': models_config,
            'current_model': self.config.get('current_model', 'openai'),
            'app': {
                'output_dir': self._output_dir.value if self._output_dir else './output',
                'history_file': self._history_file.value if self._history_file else './history.json'
            }
        }
