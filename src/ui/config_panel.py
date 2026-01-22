"""
配置面板 - API密钥和账号管理界面
"""
import flet as ft
from typing import Dict, Any, Optional, Callable


class ConfigPanel(ft.UserControl):
    """配置面板 - API密钥和账号管理"""

    def __init__(self, config: Dict[str, Any], on_save: Optional[Callable] = None):
        """
        初始化配置面板

        Args:
            config: 当前配置
            on_save: 保存回调
        """
        super().__init__()
        self.config = config
        self.on_save = on_save

        self._openai_api_key = ft.TextField(
            label="OpenAI API密钥",
            value=config.get('openai', {}).get('api_key', ''),
            password=True,
            can_reveal_password=True,
            expand=True
        )
        self._openai_api_base = ft.TextField(
            label="OpenAI API地址",
            value=config.get('openai', {}).get('api_base', 'https://api.openai.com/v1'),
            expand=True
        )
        self._openai_model = ft.TextField(
            label="OpenAI模型",
            value=config.get('openai', {}).get('model', 'gpt-4'),
            expand=True
        )
        self._netease_phone = ft.TextField(
            label="网易云音乐手机号",
            value=config.get('netease', {}).get('phone', ''),
            expand=True
        )
        self._netease_password = ft.TextField(
            label="网易云音乐密码",
            value=config.get('netease', {}).get('password', ''),
            password=True,
            can_reveal_password=True,
            expand=True
        )
        self._qishui_token = ft.TextField(
            label="汽水音乐访问令牌",
            value=config.get('qishui', {}).get('access_token', ''),
            password=True,
            can_reveal_password=True,
            expand=True
        )
        self._output_dir = ft.TextField(
            label="输出目录",
            value=config.get('app', {}).get('output_dir', './output'),
            expand=True
        )

    def build(self):
        """构建配置面板UI"""
        return ft.Container(
            content=ft.Column([
                ft.Text("配置管理", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("OpenAI配置", size=16, weight=ft.FontWeight.BOLD),
                self._openai_api_key,
                self._openai_api_base,
                self._openai_model,
                ft.Divider(),
                ft.Text("网易云音乐配置", size=16, weight=ft.FontWeight.BOLD),
                self._netease_phone,
                self._netease_password,
                ft.Divider(),
                ft.Text("汽水音乐配置", size=16, weight=ft.FontWeight.BOLD),
                self._qishui_token,
                ft.Divider(),
                ft.Text("应用配置", size=16, weight=ft.FontWeight.BOLD),
                self._output_dir,
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton(
                        "保存配置",
                        icon=ft.icons.SAVE,
                        on_click=self._on_save_click
                    ),
                    ft.ElevatedButton(
                        "取消",
                        icon=ft.icons.CANCEL,
                        on_click=self._on_cancel_click
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], scroll=ft.ScrollMode.AUTO, spacing=10),
            padding=20,
            expand=True
        )

    def _on_save_click(self, e) -> None:
        """保存按钮点击事件"""
        new_config = {
            'openai': {
                'api_key': self._openai_api_key.value,
                'api_base': self._openai_api_base.value,
                'model': self._openai_model.value
            },
            'netease': {
                'phone': self._netease_phone.value,
                'password': self._netease_password.value
            },
            'qishui': {
                'access_token': self._qishui_token.value
            },
            'app': {
                'output_dir': self._output_dir.value,
                'history_file': self.config.get('app', {}).get('history_file', './history.json')
            }
        }

        if self.on_save:
            self.on_save(new_config)

    def _on_cancel_click(self, e) -> None:
        """取消按钮点击事件"""
        if self.page:
            self.page.close_dialog()

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置

        Returns:
            配置字典
        """
        return {
            'openai': {
                'api_key': self._openai_api_key.value,
                'api_base': self._openai_api_base.value,
                'model': self._openai_model.value
            },
            'netease': {
                'phone': self._netease_phone.value,
                'password': self._netease_password.value
            },
            'qishui': {
                'access_token': self._qishui_token.value
            },
            'app': {
                'output_dir': self._output_dir.value,
                'history_file': self.config.get('app', {}).get('history_file', './history.json')
            }
        }
