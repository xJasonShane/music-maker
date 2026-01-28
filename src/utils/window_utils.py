"""
窗口工具模块
"""
import tkinter as tk
from typing import Tuple


def get_center_position(window_width: int, window_height: int) -> Tuple[int, int]:
    """
    计算并返回使给定尺寸窗口在屏幕居中的左上角坐标。
    
    Args:
        window_width: 窗口宽度（像素）
        window_height: 窗口高度（像素）
    
    Returns:
        tuple: (x, y) 窗口左上角坐标；若计算失败则返回 (100, 100)
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
