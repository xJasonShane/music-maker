"""
音悦 - AI音乐创作桌面软件 - 主程序入口
"""
import sys
import logging
import flet as ft
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MusicMakerApp
from src.core.exceptions import ConfigException
from src.utils.window_utils import get_center_position


def setup_logging():
    """配置日志系统"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('music_maker.log', encoding='utf-8')
        ]
    )


def main(page: ft.Page):
    """
    初始化并启动主应用界面。
    
    Parameters:
        page (ft.Page): Flet 提供的页面对象，用于设置窗口属性并构建应用界面。
    
    Description:
        设置窗口大小与位置（尝试居中显示），创建 MusicMakerApp 实例并在给定页面上构建界面。
        若发生配置错误或其它启动异常，会打印错误信息并以状态码 1 退出进程。
    """
    logger = logging.getLogger(__name__)
    try:
        x, y = get_center_position(1200, 800)
        page.window_width = 1200
        page.window_height = 800
        page.window_left = x
        page.window_top = y
        
        app = MusicMakerApp()
        app.build(page)
        logger.info("应用启动成功")

    except ConfigException as e:
        logger.error(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    ft.run(main)