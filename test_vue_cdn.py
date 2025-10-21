#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Vue 3 CDN版本配置对比页面
"""

import requests
import time

def test_vue_cdn():
    """测试Vue 3 CDN版本"""
    print("测试Vue 3 CDN版本配置对比页面...")
    
    try:
        session = requests.Session()
        
        # 登录
        print("1. 登录...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        login_response = session.post("http://127.0.0.1:5000/auth/login", data=login_data, allow_redirects=True)
        print(f"   登录状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   登录成功！")
            
            # 测试Vue CDN配置对比页面
            print("2. 测试Vue CDN配置对比页面...")
            compare_response = session.get("http://127.0.0.1:5000/compare")
            print(f"   配置对比页面状态码: {compare_response.status_code}")
            
            if compare_response.status_code == 200:
                content = compare_response.text
                
                # 检查Vue 3 CDN相关元素
                vue_checks = [
                    ("Vue 3", "Vue 3框架"),
                    ("createApp", "Vue 3 Composition API"),
                    ("Element Plus", "Element Plus UI库"),
                    ("dayjs", "Day.js时间库"),
                    ("配置对比", "页面标题"),
                    ("选择设备", "设备选择功能"),
                    ("第一个备份", "备份任务选择"),
                    ("第二个备份", "备份任务选择"),
                    ("对比最新两个备份", "快速对比功能"),
                    ("对比结果", "结果展示区域")
                ]
                
                success_count = 0
                for keyword, description in vue_checks:
                    if keyword in content:
                        print(f"   {description}: 找到")
                        success_count += 1
                    else:
                        print(f"   {description}: 未找到")
                
                print(f"   Vue CDN页面检查: {success_count}/{len(vue_checks)} 通过")
                
                # 检查CDN链接
                cdn_checks = [
                    ("unpkg.com/vue@3", "Vue 3 CDN"),
                    ("unpkg.com/element-plus", "Element Plus CDN"),
                    ("unpkg.com/dayjs", "Day.js CDN")
                ]
                
                cdn_success = 0
                for cdn, description in cdn_checks:
                    if cdn in content:
                        print(f"   {description}: 找到")
                        cdn_success += 1
                    else:
                        print(f"   {description}: 未找到")
                
                print(f"   CDN链接检查: {cdn_success}/{len(cdn_checks)} 通过")
                
                # 检查JavaScript功能
                js_checks = [
                    ("handleDeviceChange", "设备选择处理"),
                    ("compareLatest", "快速对比功能"),
                    ("performCompare", "执行对比功能"),
                    ("formatTaskTime", "时间格式化"),
                    ("formatFileSize", "文件大小格式化"),
                    ("canCompare", "对比条件检查")
                ]
                
                js_success = 0
                for js_func, description in js_checks:
                    if js_func in content:
                        print(f"   {description}: 找到")
                        js_success += 1
                    else:
                        print(f"   {description}: 未找到")
                
                print(f"   JavaScript功能检查: {js_success}/{len(js_checks)} 通过")
                
                # 测试后端API
                print("3. 测试后端API...")
                apis = [
                    ("/api/device/list", "设备列表API"),
                    ("/api/backup/device/1", "设备备份API"),
                    ("/api/backup/compare/quick/1", "快速对比API")
                ]
                
                api_success = 0
                for endpoint, name in apis:
                    try:
                        response = session.get(f"http://127.0.0.1:5000{endpoint}")
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                print(f"   {name}: OK")
                                api_success += 1
                            else:
                                print(f"   {name}: 失败 ({data.get('error', '未知错误')})")
                        else:
                            print(f"   {name}: HTTP错误 ({response.status_code})")
                    except Exception as e:
                        print(f"   {name}: 错误 ({str(e)})")
                
                print(f"   后端API测试: {api_success}/{len(apis)} 成功")
                
                # 总结
                total_checks = len(vue_checks) + len(cdn_checks) + len(js_checks)
                total_success = success_count + cdn_success + js_success
                
                print("\n" + "="*50)
                print("Vue 3 CDN版本测试总结:")
                print(f"页面功能: {success_count}/{len(vue_checks)} 通过")
                print(f"CDN链接: {cdn_success}/{len(cdn_checks)} 通过")
                print(f"JavaScript: {js_success}/{len(js_checks)} 通过")
                print(f"后端API: {api_success}/{len(apis)} 成功")
                print("="*50)
                
                if total_success >= total_checks * 0.8 and api_success >= len(apis) * 0.8:
                    print("Vue 3 CDN版本配置对比页面测试成功！")
                    print("无需安装Node.js，直接通过浏览器运行！")
                    return True
                else:
                    print("部分功能测试失败，需要检查")
                    return False
            else:
                print(f"   配置对比页面加载失败: {compare_response.status_code}")
                return False
        else:
            print("   登录失败")
            return False
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_vue_cdn()
