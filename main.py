"""
AI音乐创作桌面软件 - 主程序入口
"""
import sys
import flet as ft
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MusicMakerApp
from src.core.exceptions import ConfigException


def main(page: ft.Page):
    """主函数"""
    try:
        app = MusicMakerApp()
        app.build(page)

    except ConfigException as e:
        print(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    ft.run(main)
