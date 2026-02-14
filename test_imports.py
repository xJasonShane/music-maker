"""
测试项目模块导入
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("测试音悦项目模块导入")
print("=" * 60)

modules_to_test = [
    ("配置管理", "src.config.config_manager", "config_manager"),
    ("异常类", "src.core.exceptions", None),
    ("文件管理", "src.core.file_manager", None),
    ("历史记录", "src.core.history_manager", None),
    ("AI基类", "src.ai.base", None),
    ("生成器", "src.ai.generator", None),
    ("OpenAI客户端", "src.ai.openai_client", None),
    ("音频播放器", "src.ui.audio_player", None),
    ("配置面板", "src.ui.config_panel", None),
    ("主窗口", "src.ui.main_window", None),
]

all_passed = True

for name, module_path, _ in modules_to_test:
    try:
        __import__(module_path)
        print(f"✓ {name} - 成功")
    except Exception as e:
        print(f"✗ {name} - 失败: {e}")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("所有模块导入测试通过！")
else:
    print("部分模块导入失败，请检查代码")
print("=" * 60)
