#!/usr/bin/env python3
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
