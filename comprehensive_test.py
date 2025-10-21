#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cisco设备配置备份系统 - 综合测试脚本
测试所有主要功能模块
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_status(message, status="INFO"):
    """打印状态信息"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "OK":
        print(f"[{timestamp}] [OK] {message}")
    elif status == "ERROR":
        print(f"[{timestamp}] [ERROR] {message}")
    elif status == "WARNING":
        print(f"[{timestamp}] [WARNING] {message}")
    else:
        print(f"[{timestamp}] [INFO] {message}")

def test_system_startup():
    """测试系统启动"""
    print_status("开始系统启动测试...")
    
    # 检查必要目录
    required_dirs = ['logs', 'backups', 'uploads']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print_status(f"创建目录: {dir_name}")
        else:
            print_status(f"目录存在: {dir_name}")
    
    # 检查数据库文件
    if os.path.exists('app.db'):
        print_status("数据库文件存在")
    else:
        print_status("数据库文件不存在，需要初始化", "WARNING")
    
    return True

def test_web_interface():
    """测试Web界面"""
    print_status("开始Web界面测试...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试主页
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print_status("主页访问正常")
        else:
            print_status(f"主页访问失败: {response.status_code}", "ERROR")
            return False
        
        # 测试登录页面
        response = requests.get(f"{base_url}/auth/login", timeout=5)
        if response.status_code == 200:
            print_status("登录页面访问正常")
        else:
            print_status(f"登录页面访问失败: {response.status_code}", "ERROR")
            return False
        
        # 测试设备管理页面
        response = requests.get(f"{base_url}/devices", timeout=5)
        if response.status_code == 200:
            print_status("设备管理页面访问正常")
        else:
            print_status(f"设备管理页面访问失败: {response.status_code}", "ERROR")
            return False
        
        # 测试备份历史页面
        response = requests.get(f"{base_url}/history", timeout=5)
        if response.status_code == 200:
            print_status("备份历史页面访问正常")
        else:
            print_status(f"备份历史页面访问失败: {response.status_code}", "ERROR")
            return False
        
        # 测试日志页面
        response = requests.get(f"{base_url}/logs", timeout=5)
        if response.status_code == 200:
            print_status("日志页面访问正常")
        else:
            print_status(f"日志页面访问失败: {response.status_code}", "ERROR")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_status("无法连接到Web服务器，请确保系统正在运行", "ERROR")
        return False
    except Exception as e:
        print_status(f"Web界面测试失败: {str(e)}", "ERROR")
        return False

def test_api_endpoints():
    """测试API端点"""
    print_status("开始API端点测试...")
    
    base_url = "http://localhost:5000"
    
    # 创建会话以保持登录状态
    session = requests.Session()
    
    # 先登录
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        login_response = session.post(f"{base_url}/auth/login", data=login_data, timeout=5)
        if login_response.status_code == 200:
            print_status("登录成功")
        else:
            print_status("登录失败，跳过API测试", "WARNING")
            return False
    except Exception as e:
        print_status(f"登录异常: {str(e)}", "ERROR")
        return False
    
    # 测试设备列表API
    try:
        response = session.get(f"{base_url}/api/device/list", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print_status("设备列表API正常")
                else:
                    print_status(f"设备列表API返回错误: {data.get('error')}", "ERROR")
                    return False
            except json.JSONDecodeError:
                print_status("设备列表API返回非JSON响应", "ERROR")
                return False
        else:
            print_status(f"设备列表API访问失败: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"设备列表API测试失败: {str(e)}", "ERROR")
        return False
    
    # 测试统计信息API
    try:
        response = session.get(f"{base_url}/api/statistics", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print_status("统计信息API正常")
                else:
                    print_status(f"统计信息API返回错误: {data.get('error')}", "ERROR")
                    return False
            except json.JSONDecodeError:
                print_status("统计信息API返回非JSON响应", "ERROR")
                return False
        else:
            print_status(f"统计信息API访问失败: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"统计信息API测试失败: {str(e)}", "ERROR")
        return False
    
    # 测试日志文件列表API
    try:
        response = session.get(f"{base_url}/api/logs/list", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print_status("日志文件列表API正常")
                else:
                    print_status(f"日志文件列表API返回错误: {data.get('error')}", "ERROR")
                    return False
            except json.JSONDecodeError:
                print_status("日志文件列表API返回非JSON响应", "ERROR")
                return False
        else:
            print_status(f"日志文件列表API访问失败: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"日志文件列表API测试失败: {str(e)}", "ERROR")
        return False
    
    return True

def test_device_connection():
    """测试设备连接功能"""
    print_status("开始设备连接测试...")
    
    # 测试设备连接（使用测试数据）
    test_device = {
        'ip_address': '192.168.10.99',
        'username': 'admin',
        'password': 'admin123',
        'port': 22,
        'protocol': 'ssh',
        'device_type': 'cisco_ios'
    }
    
    base_url = "http://localhost:5000"
    
    try:
        # 使用会话保持登录状态
        session = requests.Session()
        
        # 先登录
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        login_response = session.post(f"{base_url}/auth/login", data=login_data, timeout=5)
        if login_response.status_code != 200:
            print_status("登录失败，跳过设备连接测试", "WARNING")
            return False
        
        response = session.post(
            f"{base_url}/api/device/test-new",
            json=test_device,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print_status("设备连接测试成功")
                    return True
                else:
                    print_status(f"设备连接测试失败: {data.get('message')}", "WARNING")
                    return False
            except json.JSONDecodeError:
                print_status("设备连接测试返回非JSON响应", "ERROR")
                return False
        else:
            print_status(f"设备连接测试请求失败: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"设备连接测试异常: {str(e)}", "ERROR")
        return False

def test_backup_functionality():
    """测试备份功能"""
    print_status("开始备份功能测试...")
    
    # 这里可以添加备份功能测试
    # 由于需要实际的设备连接，这里只做基本检查
    print_status("备份功能测试需要实际设备连接，跳过详细测试")
    return True

def test_log_functionality():
    """测试日志功能"""
    print_status("开始日志功能测试...")
    
    # 检查日志文件
    log_dir = "logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        if log_files:
            print_status(f"找到 {len(log_files)} 个日志文件")
            for log_file in log_files:
                print_status(f"  - {log_file}")
        else:
            print_status("未找到日志文件", "WARNING")
    else:
        print_status("日志目录不存在", "ERROR")
        return False
    
    return True

def test_database_functionality():
    """测试数据库功能"""
    print_status("开始数据库功能测试...")
    
    try:
        from app import create_app
        from models import db, Device, BackupTask, User
        
        app = create_app()
        with app.app_context():
            # 测试数据库连接
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print_status("数据库连接正常")
            
            # 检查表是否存在
            device_count = Device.query.count()
            task_count = BackupTask.query.count()
            user_count = User.query.count()
            
            print_status(f"设备表: {device_count} 条记录")
            print_status(f"任务表: {task_count} 条记录")
            print_status(f"用户表: {user_count} 条记录")
            
            return True
            
    except Exception as e:
        print_status(f"数据库功能测试失败: {str(e)}", "ERROR")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Cisco设备配置备份系统 - 综合测试")
    print("=" * 60)
    
    test_results = []
    
    # 系统启动测试
    test_results.append(("系统启动", test_system_startup()))
    
    # 数据库功能测试
    test_results.append(("数据库功能", test_database_functionality()))
    
    # 日志功能测试
    test_results.append(("日志功能", test_log_functionality()))
    
    # Web界面测试
    test_results.append(("Web界面", test_web_interface()))
    
    # API端点测试
    test_results.append(("API端点", test_api_endpoints()))
    
    # 设备连接测试
    test_results.append(("设备连接", test_device_connection()))
    
    # 备份功能测试
    test_results.append(("备份功能", test_backup_functionality()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "通过" if result else "失败"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print_status("所有测试通过！系统运行正常", "OK")
    else:
        print_status(f"有 {total - passed} 项测试失败，请检查系统配置", "ERROR")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
