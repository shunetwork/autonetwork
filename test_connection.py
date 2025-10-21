#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试连接API
"""

import requests
import json

def test_api():
    """测试API连接"""
    url = "http://localhost:5000/api/device/test-new"
    data = {
        "ip_address": "192.168.1.1",
        "username": "admin", 
        "password": "admin123",
        "port": 22,
        "protocol": "ssh",
        "device_type": "cisco_ios"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"API调用成功: {result}")
        else:
            print(f"API调用失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保系统正在运行")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api()


