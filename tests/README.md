# 测试脚本目录

本目录包含Cisco设备配置备份系统的各种测试脚本。

## 测试脚本说明

### 系统测试脚本
- `test_system.py` - 系统功能综合测试
- `comprehensive_test.py` - 系统完整性测试
- `system_enhancement.py` - 系统增强功能测试

### 设备连接测试
- `test_connection.py` - 设备连接测试
- `check_device.py` - 设备状态检查
- `test_show_run.py` - 设备配置显示测试

### 备份功能测试
- `test_backup.py` - 备份功能测试
- `test_full_backup.py` - 完整备份测试
- `create_backup.py` - 创建备份测试

### 计划任务测试
- `test_scheduler.py` - 计划任务功能测试

### 前端测试
- `test_api.html` - API接口测试页面

## 使用方法

### 运行系统测试
```bash
python test_system.py
```

### 运行设备连接测试
```bash
python test_connection.py
```

### 运行备份功能测试
```bash
python test_backup.py
```

### 运行计划任务测试
```bash
python test_scheduler.py
```

## 注意事项

1. 运行测试前请确保系统已启动
2. 确保数据库连接正常
3. 部分测试需要有效的设备配置
4. 测试脚本会创建测试数据，请注意数据清理

## 测试环境要求

- Python 3.8+
- Flask应用运行中
- 数据库连接正常
- 网络连接正常（设备测试需要）
