#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整备份流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Device, BackupTask
from backup_service import BackupService

def test_full_backup():
    """测试完整备份流程"""
    with app.app_context():
        # 获取第一个设备
        device = Device.query.first()
        if not device:
            print("没有设备")
            return
        
        print(f"为设备 {device.ip_address} 创建完整备份任务")
        
        # 创建备份服务
        backup_service = BackupService()
        
        # 创建备份任务
        result = backup_service.backup_single_device(
            device_id=device.id,
            user_id=1,  # admin用户
            backup_command='show running-config',  # 使用show running-config命令
            task_type='manual'
        )
        
        print(f"备份任务创建结果: {result}")
        
        if result['success']:
            task_id = result['task_id']
            print(f"任务ID: {task_id}")
            
            # 等待任务完成
            import time
            for i in range(30):  # 最多等待30秒
                time.sleep(1)
                task = BackupTask.query.get(task_id)
                print(f"任务状态: {task.status}")
                
                if task.status in ['success', 'failed']:
                    break
            
            # 最终状态
            task = BackupTask.query.get(task_id)
            print(f"最终状态: {task.status}")
            if task.status == 'success':
                print(f"备份文件: {task.file_path}")
                print(f"文件大小: {task.file_size} 字节")
                print(f"文件哈希: {task.file_hash}")
            elif task.status == 'failed':
                print(f"失败原因: {task.error_message}")
        else:
            print(f"创建任务失败: {result['error']}")

if __name__ == "__main__":
    test_full_backup()


