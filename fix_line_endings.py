"""
修复所有Python文件的换行符问题
将Windows的CRLF(\r\n)转换为LF(\n)
"""
import os
from pathlib import Path

def fix_line_endings(file_path: Path) -> bool:
    """
    修复单个文件的换行符
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否需要修复
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 检查是否包含 CRLF
        if b'\r\n' in content:
            # 替换 CRLF 为 LF
            new_content = content.replace(b'\r\n', b'\n')
            
            # 再检查是否有孤立的 CR，也替换掉
            new_content = new_content.replace(b'\r', b'\n')
            
            with open(file_path, 'wb') as f:
                f.write(new_content)
            
            print(f"✓ 修复换行符: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"✗ 处理失败 {file_path}: {e}")
        return False

def main():
    project_root = Path(__file__).parent
    print("=" * 60)
    print("修复代码换行符 (CRLF → LF)")
    print("=" * 60)
    
    # 需要处理的目录
    target_dirs = ['src', '.']
    exclude_dirs = ['.venv', '__pycache__', '.git', 'build', 'dist']
    
    python_files = []
    
    # 查找所有 Python 文件，但排除虚拟环境等目录
    for file_path in project_root.rglob('*.py'):
        # 检查是否在排除目录中
        exclude = False
        for exclude_dir in exclude_dirs:
            if exclude_dir in file_path.parts:
                exclude = True
                break
        
        if not exclude:
            python_files.append(file_path)
    
    print(f"\n找到 {len(python_files)} 个 Python 文件\n")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_line_endings(file_path):
            fixed_count += 1
    
    print(f"\n完成！共修复 {fixed_count} 个文件")

if __name__ == "__main__":
    main()
