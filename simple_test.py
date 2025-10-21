#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化系统测试脚本
"""

import os
import sys
from pathlib import Path

def test_file_structure():
    """测试文件结构"""
    print("测试文件结构...")
    
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
        print(f"X 缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("OK 所有必需文件存在")
    
    if missing_dirs:
        print(f"X 缺少目录: {', '.join(missing_dirs)}")
        return False
    else:
        print("OK 所有必需目录存在")
    
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
        print(f"X 缺少模板文件: {', '.join(missing_templates)}")
        return False
    else:
        print("OK 所有模板文件存在")
    
    return True

def test_python_syntax():
    """测试Python语法"""
    print("\n测试Python语法...")
    
    python_files = [
        'app.py',
        'models.py',
        'device_manager.py',
        'backup_service.py',
        'scheduler.py',
        'auth.py',
        'api.py',
        'import_service.py',
        'config.py',
        'run.py'
    ]
    
    syntax_errors = []
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                compile(f.read(), file, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file}: {e}")
    
    if syntax_errors:
        print(f"X 语法错误: {', '.join(syntax_errors)}")
        return False
    else:
        print("OK 所有Python文件语法正确")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("Cisco设备配置备份系统 - 简化测试")
    print("=" * 60)
    
    tests = [
        ("文件结构", test_file_structure),
        ("模板文件", test_templates),
        ("Python语法", test_python_syntax)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"OK {test_name} 测试通过")
        else:
            print(f"X {test_name} 测试失败")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("基础测试通过！")
        print("\n下一步:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动系统: python run.py")
    else:
        print("部分测试失败，请检查错误信息。")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
