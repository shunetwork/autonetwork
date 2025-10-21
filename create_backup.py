#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建新的备份任务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Device, BackupTask
from backup_service import BackupService

def create_backup():
    """创建备份任务"""
    with app.app_context():
        # 获取第一个设备
        device = Device.query.first()
        if not device:
            print("没有设备")
            return
        
        print(f"为设备 {device.ip_address} 创建备份任务")
        
        # 创建备份服务
        backup_service = BackupService()
        
        # 创建备份任务
        result = backup_service.backup_single_device(
            device_id=device.id,
            user_id=1,  # admin用户
            backup_command='show version',  # 使用简单命令
            task_type='manual'
        )
        
        print(f"备份任务创建结果: {result}")
        
        # 等待一下
        import time
        time.sleep(2)
        
        # 检查任务状态
        task = BackupTask.query.get(result['task_id'])
        print(f"任务状态: {task.status}")
        if task.error_message:
            print(f"错误信息: {task.error_message}")

if __name__ == "__main__":
    create_backup()


