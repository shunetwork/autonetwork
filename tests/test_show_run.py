#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试show running-config命令
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Device
from device_manager import DeviceManager

def test_show_run():
    """测试show running-config命令"""
    with app.app_context():
        # 获取第一个设备
        device = Device.query.first()
        if not device:
            print("没有设备")
            return
        
        print(f"测试设备: {device.ip_address}")
        
        # 构建设备信息
        device_info = {
            'id': device.id,
            'ip_address': device.ip_address,
            'username': device.username,
            'password_encrypted': device.password_encrypted,
            'enable_password_encrypted': device.enable_password_encrypted,
            'device_type': device.device_type,
            'port': device.port,
            'protocol': device.protocol
        }
        
        # 创建设备管理器
        device_manager = DeviceManager()
        
        # 获取连接
        connection = device_manager.get_connection(device_info)
        if not connection:
            print("无法建立连接")
            return
        
        print("连接成功，开始执行show running-config...")
        
        # 执行命令
        result = connection.execute_command('show running-config')
        
        if result['success']:
            print(f"命令执行成功，输出长度: {len(result['output'])}")
            print("前500字符:")
            print(result['output'][:500])
            print("...")
        else:
            print(f"命令执行失败: {result['error']}")
        
        # 断开连接
        connection.disconnect()

if __name__ == "__main__":
    test_show_run()


