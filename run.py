#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cisco设备配置备份系统启动脚本
"""

import os
import sys
from app import app, db, scheduler

def main():
    """主函数"""
    print("=" * 60)
    print("Cisco设备配置备份系统")
    print("=" * 60)
    
    # 检查环境变量
    if not os.environ.get('SECRET_KEY'):
        print("警告: 未设置SECRET_KEY环境变量，使用默认密钥（生产环境请设置安全密钥）")
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    if not os.environ.get('ENCRYPTION_KEY'):
        print("警告: 未设置ENCRYPTION_KEY环境变量，使用默认密钥（生产环境请设置安全密钥）")
        os.environ['ENCRYPTION_KEY'] = 'default-encryption-key-change-in-production'
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # 初始化数据库
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员用户
        from models import User
        from werkzeug.security import generate_password_hash
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("OK 创建默认管理员用户: admin/admin123")
        else:
            print("OK 管理员用户已存在")
    
    # 启动调度器
    try:
        scheduler.start()
        print("OK 备份调度器已启动")
    except Exception as e:
        print(f"X 启动调度器失败: {e}")
    
    print("\n系统启动完成！")
    print("访问地址: http://localhost:5000")
    print("默认账号: admin / admin123")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        scheduler.shutdown()
        print("服务已停止")

if __name__ == '__main__':
    main()
