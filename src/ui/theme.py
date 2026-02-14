"""
UI设计系统 - 简化版，确保Flet兼容性
"""
import flet as ft


class DesignSystem:
    """设计系统 - 统一的UI规范"""
    
    # 颜色系统
    class Colors:
        """配色方案"""
        PRIMARY = ft.Colors.BLUE_600
        PRIMARY_LIGHT = ft.Colors.BLUE_50
        PRIMARY_DARK = ft.Colors.BLUE_800
        SUCCESS = ft.Colors.GREEN_600
        SUCCESS_LIGHT = ft.Colors.GREEN_50
        WARNING = ft.Colors.ORANGE_600
        WARNING_LIGHT = ft.Colors.ORANGE_50
        ERROR = ft.Colors.RED_600
        ERROR_LIGHT = ft.Colors.RED_50
        WHITE = ft.Colors.WHITE
        GREY_50 = ft.Colors.GREY_50
        GREY_100 = ft.Colors.GREY_100
        GREY_200 = ft.Colors.GREY_200
        GREY_300 = ft.Colors.GREY_300
        GREY_400 = ft.Colors.GREY_400
        GREY_500 = ft.Colors.GREY_500
        GREY_600 = ft.Colors.GREY_600
        GREY_700 = ft.Colors.GREY_700
        GREY_800 = ft.Colors.GREY_800
        GREY_900 = ft.Colors.GREY_900
        SURFACE = WHITE
        SURFACE_VARIANT = GREY_50
        BACKGROUND = GREY_50
        TEXT_PRIMARY = GREY_900
        TEXT_SECONDARY = GREY_600
        TEXT_DISABLED = GREY_400
    
    # 间距系统
    class Spacing:
        """间距规范"""
        XS = 4
        SM = 8
        MD = 12
        LG = 16
        XL = 24
        XXL = 32
        XXXL = 48
    
    # 圆角系统
    class Radius:
        """圆角规范"""
        SM = 4
        MD = 8
        LG = 12
        XL = 16
        FULL = 999
