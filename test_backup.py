#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试备份功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, BackupTask, Device
from backup_service import BackupService

def test_backup():
    """测试备份功能"""
    with app.app_context():
        # 查看所有任务
        tasks = BackupTask.query.all()
        print(f"总任务数: {len(tasks)}")
        
        for task in tasks:
            print(f"任务 {task.id}: 状态={task.status}, 设备={task.device.ip_address if task.device else 'None'}")
        
        # 手动执行一个pending任务
        pending_tasks = BackupTask.query.filter_by(status='pending').all()
        if pending_tasks:
            task = pending_tasks[0]
            print(f"手动执行任务 {task.id}")
            
            backup_service = BackupService()
            backup_service._execute_backup(task.id)
            
            # 重新查询任务状态
            task = BackupTask.query.get(task.id)
            print(f"任务 {task.id} 新状态: {task.status}")
        else:
            print("没有pending任务")

if __name__ == "__main__":
    test_backup()


