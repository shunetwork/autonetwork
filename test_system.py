#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
用于验证Cisco设备配置备份系统的基本功能
"""

import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from app import app, db
        print("✓ Flask应用导入成功")
    except Exception as e:
        print(f"✗ Flask应用导入失败: {e}")
        return False
    
    try:
        from models import User, Device, BackupTask
        print("✓ 数据模型导入成功")
    except Exception as e:
        print(f"✗ 数据模型导入失败: {e}")
        return False
    
    try:
        from device_manager import DeviceManager
        print("✓ 设备管理器导入成功")
    except Exception as e:
        print(f"✗ 设备管理器导入失败: {e}")
        return False
    
    try:
        from backup_service import BackupService
        print("✓ 备份服务导入成功")
    except Exception as e:
        print(f"✗ 备份服务导入失败: {e}")
        return False
    
    try:
        from scheduler import BackupScheduler
        print("✓ 调度器导入成功")
    except Exception as e:
        print(f"✗ 调度器导入失败: {e}")
        return False
    
    return True

def test_database():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # 测试数据库连接
            db.create_all()
            print("✓ 数据库连接成功")
            
            # 测试用户查询
            user_count = User.query.count()
            print(f"✓ 用户查询成功，当前用户数: {user_count}")
            
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def test_import_service():
    """测试导入服务"""
    print("\n测试导入服务...")
    
    try:
        from import_service import ImportService
        
        # 创建测试数据
        test_data = {
            'ip_address': ['192.168.1.1', '192.168.1.2'],
            'username': ['admin', 'admin'],
            'password': ['password123', 'password456'],
            'alias': ['Router-01', 'Switch-01'],
            'port': [22, 22],
            'protocol': ['ssh', 'ssh'],
            'device_type': ['cisco_ios', 'cisco_ios']
        }
        
        df = pd.DataFrame(test_data)
        
        # 创建临时CSV文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            # 测试导入服务
            import_service = ImportService()
            
            # 测试模板创建
            template_data = import_service.create_template_file('csv')
            if template_data:
                print("✓ 模板文件创建成功")
            else:
                print("✗ 模板文件创建失败")
                return False
            
            # 测试数据验证
            validation_result = import_service.validate_import_data(test_data)
            if validation_result['valid']:
                print("✓ 数据验证成功")
            else:
                print(f"✗ 数据验证失败: {validation_result['errors']}")
                return False
            
            print("✓ 导入服务测试成功")
            return True
            
        finally:
            # 清理临时文件
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"✗ 导入服务测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n测试文件结构...")
    
    required_files = [
        'app.py',
        'models.py',
        'device_manager.py',
        'backup_service.py',
        'scheduler.py',
        'auth.py',
        'api.py',
        'import_service.py',
        'config.py',
        'run.py',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'templates',
        'logs',
        'backups',
        'uploads'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    missing_dirs = []
    for dir in required_dirs:
        if not Path(dir).exists():
            missing_dirs.append(dir)
    
    if missing_files:
        print(f"✗ 缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✓ 所有必需文件存在")
    
    if missing_dirs:
        print(f"✗ 缺少目录: {', '.join(missing_dirs)}")
        return False
    else:
        print("✓ 所有必需目录存在")
    
    return True

def test_templates():
    """测试模板文件"""
    print("\n测试模板文件...")
    
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/backup_single.html',
        'templates/backup_batch.html',
        'templates/devices.html',
        'templates/history.html',
        'templates/settings.html',
        'templates/logs.html',
        'templates/auth/login.html'
    ]
    
    missing_templates = []
    for template in template_files:
        if not Path(template).exists():
            missing_templates.append(template)
    
    if missing_templates:
        print(f"✗ 缺少模板文件: {', '.join(missing_templates)}")
        return False
    else:
        print("✓ 所有模板文件存在")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("Cisco设备配置备份系统 - 系统测试")
    print("=" * 60)
    
    tests = [
        ("文件结构", test_file_structure),
        ("模板文件", test_templates),
        ("模块导入", test_imports),
        ("数据库连接", test_database),
        ("导入服务", test_import_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} 测试通过")
        else:
            print(f"✗ {test_name} 测试失败")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常启动。")
        print("\n启动命令:")
        print("python run.py")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())


