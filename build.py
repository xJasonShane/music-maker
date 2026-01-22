"""
打包脚本 - 使用PyInstaller打包为跨平台可执行文件
"""
import os
import sys
import subprocess
from pathlib import Path


def build_executable():
    """打包为可执行文件"""
    print("开始打包AI音乐创作软件...")

    project_root = Path(__file__).parent
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"

    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)

    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)

    pyinstaller_args = [
        "pyinstaller",
        "--name=MusicMaker",
        "--windowed",
        "--onefile",
        "--clean",
        "--noconfirm",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}",
        "--add-data=src;src",
        "--hidden-import=flet",
        "--hidden-import=requests",
        "--hidden-import=dotenv",
        "--hidden-import=midiutil",
        "--hidden-import=librosa",
        "main.py"
    ]

    print("执行PyInstaller命令...")
    print(" ".join(pyinstaller_args))

    try:
        subprocess.run(pyinstaller_args, check=True)
        print(f"\n打包成功！")
        print(f"可执行文件位置: {dist_dir / 'MusicMaker.exe'}")

        print("\n打包说明:")
        print("1. 可执行文件位于 dist/ 目录")
        print("2. 首次运行需要创建 .env 配置文件")
        print("3. 将 .env.example 复制为 .env 并填写配置")
        print("4. 确保 output 目录存在用于保存生成的文件")

    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
