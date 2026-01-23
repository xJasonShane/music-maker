"""
音悦 - AI音乐创作桌面软件 - 主程序入口
"""
import sys
import flet as ft
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MusicMakerApp
from src.core.exceptions import ConfigException


def get_center_position(window_width: int, window_height: int) -> tuple:
    """
    获取窗口居中位置

    Args:
        window_width: 窗口宽度
        window_height: 窗口高度

    Returns:
        (x, y) 窗口左上角坐标
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


def main(page: ft.Page):
    """主函数"""
    try:
        x, y = get_center_position(1200, 800)
        page.window_width = 1200
        page.window_height = 800
        page.window_left = x
        page.window_top = y
        
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
