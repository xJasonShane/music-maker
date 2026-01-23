"""
配置面板 - 支持多模型配置
"""
import flet as ft
from typing import Dict, Any, Optional, Callable, List


class ConfigPanel:
    """配置面板 - 支持多模型配置"""

    def __init__(self, config: Dict[str, Any], on_save: Optional[Callable] = None):
        """
        初始化配置面板

        Args:
            config: 当前配置
            on_save: 保存回调
        """
        self.config = config
        self.on_save = on_save
        self._page = None
        self._model_configs: Dict[str, Dict[str, ft.Control]] = {}
        self._output_dir = None
        self._history_file = None

    def build(self, page: ft.Page):
        """
        构建并返回用于显示和编辑多模型配置的面板容器，并将传入的页面对象保存到实例以便后续刷新或关闭对话框。
        
        Parameters:
            page (ft.Page): 父页面对象，方法会将其保存到 self._page 以便后续刷新界面和关闭对话框。
        
        Returns:
            ft.Container: 包含模型配置区、应用配置字段和保存/取消按钮的容器，用于在界面中显示配置面板。
        """
        self._page = page

        models_config = self.config.get('models', {})
        current_model = self.config.get('current_model', 'openai')
        app_config = self.config.get('app', {})

        model_fields = []
        for model_id, model_config in models_config.items():
            model_fields.append(self._create_model_field(model_id, model_config, current_model))

        self._output_dir = ft.TextField(
            label="输出目录",
            value=app_config.get('output_dir', './output'),
            expand=True
        )

        self._history_file = ft.TextField(
            label="历史记录文件",
            value=app_config.get('history_file', './history.json'),
            expand=True
        )

        content = ft.Column([
            ft.Text("配置管理", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            ft.Container(
                content=ft.Text("模型配置", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                padding=ft.padding.only(bottom=10)
            ),
            ft.Column(model_fields, spacing=15),
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            ft.Container(
                content=ft.Text("应用配置", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                padding=ft.padding.only(bottom=10)
            ),
            self._output_dir,
            self._history_file,
            ft.Divider(height=2, color=ft.Colors.BLUE_200),
            ft.Row([
                ft.ElevatedButton(
                "保存配置",
                icon=ft.icons.Icons.SAVE,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=self._on_save_click
            ),
            ft.Container(width=10),
            ft.ElevatedButton(
                "取消",
                icon=ft.icons.Icons.CANCEL,
                bgcolor=ft.Colors.GREY_400,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=self._on_cancel_click
            )
            ], alignment=ft.MainAxisAlignment.END)
        ], scroll=ft.ScrollMode.AUTO, spacing=15)

        return ft.Container(
            content=content,
            padding=20,
            width=600,
            height=500
        )

    def _create_model_field(self, model_id: str, model_config: Dict[str, Any], current_model: str) -> ft.Container:
        """
        创建模型配置字段

        Args:
            model_id: 模型ID
            model_config: 模型配置
            current_model: 当前选中的模型ID

        Returns:
            配置容器
        """
        model_name = model_config.get('name', model_id)
        is_current = model_id == current_model

        enabled_switch = ft.Switch(
            label="启用",
            value=model_config.get('enabled', False),
            on_change=lambda e, mid=model_id: self._on_model_enabled_change(mid, e.control.value),
            active_color=ft.Colors.BLUE_600
        )

        api_key_field = ft.TextField(
            label=f"{model_name} API密钥",
            value=model_config.get('api_key', ''),
            password=True,
            can_reveal_password=True,
            expand=True,
            border_radius=8,
            filled=True
        )

        api_base_field = ft.TextField(
            label=f"{model_name} API地址",
            value=model_config.get('api_base', ''),
            expand=True,
            border_radius=8,
            filled=True
        )

        model_field = ft.TextField(
            label=f"{model_name} 模型名称",
            value=model_config.get('model', ''),
            expand=True,
            border_radius=8,
            filled=True
        )

        select_button = ft.IconButton(
            icon=ft.icons.Icons.CHECK_CIRCLE if is_current else ft.icons.Icons.RADIO_BUTTON_UNCHECKED,
            tooltip="选择此模型" if not is_current else "当前模型",
            icon_color=ft.Colors.BLUE_600 if is_current else ft.Colors.GREY_400,
            icon_size=28,
            on_click=lambda e, mid=model_id: self._on_model_select(mid),
            disabled=is_current
        )

        self._model_configs[model_id] = {
            'enabled': enabled_switch,
            'api_key': api_key_field,
            'api_base': api_base_field,
            'model': model_field
        }

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(model_name, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Container(expand=True),
                    enabled_switch,
                    select_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Column([
                    api_key_field,
                    api_base_field,
                    model_field
                ], spacing=10)
            ], spacing=10),
            padding=20,
            border=ft.border.all(3, ft.Colors.BLUE_600 if is_current else ft.Colors.GREY_300),
            border_radius=12,
            bgcolor=ft.Colors.BLUE_50 if is_current else ft.Colors.WHITE
        )

    def _on_model_enabled_change(self, model_id: str, enabled: bool) -> None:
        """
        模型启用状态改变

        Args:
            model_id: 模型ID
            enabled: 是否启用
        """
        if model_id in self._model_configs:
            self._model_configs[model_id]['enabled'].value = enabled

    def _on_model_select(self, model_id: str) -> None:
        """
        选择模型

        Args:
            model_id: 模型ID
        """
        self.config['current_model'] = model_id
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        """刷新UI"""
        if self._page:
            dialog_content = self.build(self._page)
            if hasattr(self._page, 'dialog') and self._page.dialog:
                self._page.dialog.content = dialog_content
                self._page.update()

    def _on_save_click(self, e) -> None:
        """保存按钮点击事件"""
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

    def _on_cancel_click(self, e) -> None:
        """取消按钮点击事件"""
        if self._page:
            self._page.close_dialog()

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置

        Returns:
            配置字典
        """
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
                'output_dir': self._output_dir.value,
                'history_file': self._history_file.value
            }
        }