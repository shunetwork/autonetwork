#!/usr/bin/env python3
import requests
import json

# 测试系统日志API
def test_logs_api():
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
            # 发送请求到日志API
            url = "http://127.0.0.1:5000/api/logs/entries?page=1&per_page=5"
            response = session.get(url)
            
            print(f"API状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"成功: {data.get('success', False)}")
                    print(f"总数: {data.get('total', 0)}")
                    
                    logs = data.get('logs', [])
                    print(f"日志条目数: {len(logs)}")
                    
                    if logs:
                        print("\n前3条日志的时间戳:")
                        for i, log in enumerate(logs[:3]):
                            print(f"日志 {i+1}:")
                            print(f"  timestamp: {log.get('timestamp', 'N/A')}")
                            print(f"  level: {log.get('level', 'N/A')}")
                            print(f"  message: {log.get('message', 'N/A')[:50]}...")
                            print()
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"原始响应: {response.text}")
        else:
            print(f"登录失败: {login_response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_logs_api()
