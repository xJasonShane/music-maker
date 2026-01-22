"""
AI音乐创作桌面软件 - 主程序入口
"""
import sys
import flet as ft
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MusicMakerApp
from src.core.exceptions import ConfigException


def main():
    """主函数"""
    try:
        app = MusicMakerApp()

        def route_change(route):
            page.views.clear()
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("AI音乐创作软件"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ]
                )
            )
            page.update()

        def view_pop(view):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        page = ft.Page(on_route_change=route_change, on_view_pop=view_pop)
        page.go("/")

        app.build(page)

    except ConfigException as e:
        print(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    ft.app(target=main)
