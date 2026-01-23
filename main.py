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
    计算并返回使给定尺寸窗口在屏幕居中的左上角坐标。
    
    Parameters:
        window_width (int): 窗口宽度（像素）。
        window_height (int): 窗口高度（像素）。
    
    Returns:
        tuple: (x, y) 窗口左上角坐标；若计算失败则返回 (100, 100) 作为后备坐标。
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
    """
    初始化并启动主应用界面。
    
    Parameters:
        page (ft.Page): Flet 提供的页面对象，用于设置窗口属性并构建应用界面。
    
    Description:
        设置窗口大小与位置（尝试居中显示），创建 MusicMakerApp 实例并在给定页面上构建界面。
        若发生配置错误或其它启动异常，会打印错误信息并以状态码 1 退出进程。
    """
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