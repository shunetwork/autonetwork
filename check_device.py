#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查设备信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Device

def check_device():
    """检查设备信息"""
    with app.app_context():
        devices = Device.query.all()
        print(f"设备数量: {len(devices)}")
        
        for device in devices:
            print(f"设备 {device.id}:")
            print(f"  IP: {device.ip_address}")
            print(f"  用户名: {device.username}")
            print(f"  密码长度: {len(device.password_encrypted)}")
            print(f"  密码前10字符: {device.password_encrypted[:10]}")
            print(f"  设备类型: {device.device_type}")
            print(f"  协议: {device.protocol}")
            print(f"  端口: {device.port}")
            print()

if __name__ == "__main__":
    check_device()


