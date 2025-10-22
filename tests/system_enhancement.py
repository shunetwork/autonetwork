#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统完善脚本
修复潜在问题并优化系统
"""

import os
import sys
import shutil
from pathlib import Path

def print_status(message, status="INFO"):
    """打印状态信息"""
    if status == "OK":
        print(f"[OK] {message}")
    elif status == "ERROR":
        print(f"[ERROR] {message}")
    elif status == "WARNING":
        print(f"[WARNING] {message}")
    else:
        print(f"[INFO] {message}")

def create_missing_directories():
    """创建缺失的目录"""
    print_status("检查并创建必要目录...")
    
    required_dirs = [
        'logs',
        'backups', 
        'uploads',
        'backups/test',
        'backups/192.168.10.99'
    ]
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print_status(f"创建目录: {dir_name}")
        else:
            print_status(f"目录已存在: {dir_name}")

def fix_log_file_encoding():
    """修复日志文件编码问题"""
    print_status("检查日志文件编码...")
    
    log_dir = Path('logs')
    if log_dir.exists():
        for log_file in log_dir.glob('*.log'):
            try:
                # 尝试读取文件检查编码
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print_status(f"日志文件 {log_file.name} 编码正常")
            except UnicodeDecodeError:
                try:
                    # 尝试GBK编码
                    with open(log_file, 'r', encoding='gbk') as f:
                        content = f.read()
                    print_status(f"日志文件 {log_file.name} 使用GBK编码")
                except Exception as e:
                    print_status(f"日志文件 {log_file.name} 编码问题: {str(e)}", "WARNING")

def optimize_database():
    """优化数据库"""
    print_status("检查数据库状态...")
    
    db_file = 'app.db'
    if os.path.exists(db_file):
        file_size = os.path.getsize(db_file)
        print_status(f"数据库文件大小: {file_size} 字节")
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            print_status("数据库文件较大，建议清理", "WARNING")
    else:
        print_status("数据库文件不存在，需要初始化", "WARNING")

def check_system_resources():
    """检查系统资源"""
    print_status("检查系统资源...")
    
    # 检查磁盘空间
    import shutil
    total, used, free = shutil.disk_usage('.')
    free_gb = free // (1024**3)
    print_status(f"可用磁盘空间: {free_gb} GB")
    
    if free_gb < 1:
        print_status("磁盘空间不足", "WARNING")
    
    # 检查Python版本
    python_version = sys.version_info
    print_status(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print_status("Python版本过低，建议升级到3.7+", "WARNING")

def create_system_info():
    """创建系统信息文件"""
    print_status("创建系统信息文件...")
    
    info_content = f"""
# Cisco设备配置备份系统 - 系统信息

## 系统环境
- Python版本: {sys.version}
- 操作系统: {os.name}
- 工作目录: {os.getcwd()}

## 目录结构
"""
    
    # 扫描目录结构
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        info_content += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # 只显示前5个文件
            info_content += f"{subindent}{file}\n"
        if len(files) > 5:
            info_content += f"{subindent}... 还有 {len(files) - 5} 个文件\n"
    
    with open('system_info.md', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print_status("系统信息文件已创建: system_info.md")

def cleanup_temp_files():
    """清理临时文件"""
    print_status("清理临时文件...")
    
    temp_patterns = [
        '*.tmp',
        '*.temp',
        '__pycache__',
        '*.pyc',
        '*.pyo'
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        for file_path in Path('.').glob(f'**/{pattern}'):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    cleaned_count += 1
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    cleaned_count += 1
            except Exception as e:
                print_status(f"清理文件失败 {file_path}: {str(e)}", "WARNING")
    
    print_status(f"清理了 {cleaned_count} 个临时文件")

def create_backup_script():
    """创建备份脚本"""
    print_status("创建系统备份脚本...")
    
    backup_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统备份脚本
"""

import os
import shutil
import datetime
from pathlib import Path

def backup_system():
    """备份系统数据"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"system_backup_{timestamp}"
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 备份重要文件
    important_files = [
        'app.py',
        'models.py',
        'device_manager.py',
        'backup_service.py',
        'api.py',
        'auth.py',
        'scheduler.py',
        'requirements.txt',
        'app.db'
    ]
    
    for file_name in important_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, backup_dir)
            print(f"备份文件: {file_name}")
    
    # 备份目录
    important_dirs = ['logs', 'backups']
    for dir_name in important_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(backup_dir, dir_name))
            print(f"备份目录: {dir_name}")
    
    print(f"系统备份完成: {backup_dir}")

if __name__ == "__main__":
    backup_system()
'''
    
    with open('backup_system.py', 'w', encoding='utf-8') as f:
        f.write(backup_script)
    
    print_status("系统备份脚本已创建: backup_system.py")

def main():
    """主函数"""
    print("=" * 60)
    print("Cisco设备配置备份系统 - 系统完善")
    print("=" * 60)
    
    # 创建必要目录
    create_missing_directories()
    
    # 修复日志文件编码
    fix_log_file_encoding()
    
    # 优化数据库
    optimize_database()
    
    # 检查系统资源
    check_system_resources()
    
    # 创建系统信息
    create_system_info()
    
    # 清理临时文件
    cleanup_temp_files()
    
    # 创建备份脚本
    create_backup_script()
    
    print("\n" + "=" * 60)
    print_status("系统完善完成！", "OK")
    print("=" * 60)

if __name__ == "__main__":
    main()
