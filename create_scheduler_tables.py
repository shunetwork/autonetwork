#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建计划任务相关数据库表
"""

from app import app, db
from models import ScheduledTask, TaskExecution

def create_scheduler_tables():
    """创建计划任务相关表"""
    with app.app_context():
        try:
            # 创建计划任务表
            db.create_all()
            print("OK - 计划任务相关表创建成功！")
            print("已创建的表：")
            print("   - scheduled_tasks (计划任务表)")
            print("   - task_executions (任务执行记录表)")
        except Exception as e:
            print(f"ERROR - 创建表失败: {e}")

if __name__ == "__main__":
    create_scheduler_tables()
