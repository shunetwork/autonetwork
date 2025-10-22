#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试计划任务功能
"""

import requests
import json

def test_scheduler_api():
    """测试计划任务API"""
    try:
        # 先登录获取session
        session = requests.Session()
        
        # 登录
        login_url = "http://127.0.0.1:5000/auth/login"
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        login_response = session.post(login_url, data=login_data)
        print(f"登录状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # 测试获取调度器选项
            print("\n=== 测试获取调度器选项 ===")
            options_response = session.get("http://127.0.0.1:5000/api/scheduler/options")
            print(f"选项API状态码: {options_response.status_code}")
            if options_response.status_code == 200:
                options_data = options_response.json()
                print(f"选项数据: {json.dumps(options_data, ensure_ascii=False, indent=2)}")
            
            # 测试创建计划任务
            print("\n=== 测试创建计划任务 ===")
            task_data = {
                "name": "测试每日备份",
                "description": "测试用的每日备份任务",
                "task_type": "backup",
                "frequency_type": "daily",
                "frequency_config": {
                    "type": "daily",
                    "hour": 2,
                    "minute": 0
                },
                "target_devices": [1],  # 假设设备ID为1
                "backup_command": "show running-config",
                "is_active": True
            }
            
            create_response = session.post(
                "http://127.0.0.1:5000/api/scheduler/tasks",
                json=task_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"创建任务状态码: {create_response.status_code}")
            print(f"创建任务响应: {create_response.text}")
            
            # 测试获取计划任务列表
            print("\n=== 测试获取计划任务列表 ===")
            tasks_response = session.get("http://127.0.0.1:5000/api/scheduler/tasks")
            print(f"任务列表状态码: {tasks_response.status_code}")
            if tasks_response.status_code == 200:
                tasks_data = tasks_response.json()
                print(f"任务列表: {json.dumps(tasks_data, ensure_ascii=False, indent=2)}")
            
        else:
            print(f"登录失败: {login_response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_scheduler_api()
