#!/usr/bin/env python3
"""
生产环境启动脚本
使用Gunicorn作为WSGI服务器
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # 设置环境变量
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # 获取配置
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("=" * 60)
    print("Cisco设备备份管理系统")
    print("=" * 60)
    print("环境: 生产环境")
    print(f"地址: http://{host}:{port}")
    print("默认账号: admin / admin123")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 启动应用
    app.run(host=host, port=port, debug=debug)
