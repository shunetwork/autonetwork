# Cisco设备配置备份系统

一个功能完整的Cisco设备配置备份管理系统，支持单设备和批量备份、计划任务、差异比较等功能。

## 功能特性

### 🔧 核心功能
- **单设备备份**: 支持SSH/Telnet连接，执行自定义备份命令
- **批量备份**: CSV/Excel文件导入，支持大量设备批量操作
- **计划任务**: CRON式调度，支持定时自动备份
- **配置差异**: 自动比较配置变化，生成差异报告
- **文件管理**: 自动文件命名、压缩存储、哈希校验

### 🛡️ 安全特性
- **密码加密**: 设备密码加密存储，支持Vault/KMS集成
- **权限控制**: 基于角色的访问控制
- **审计日志**: 完整的操作日志和审计跟踪
- **HTTPS支持**: 安全的Web传输

### 📊 管理功能
- **设备管理**: 设备信息管理、连接测试
- **任务监控**: 实时任务状态、进度跟踪
- **历史记录**: 备份历史查询、文件下载
- **统计分析**: 备份统计、成功率分析

## 技术架构

### 后端技术
- **Flask**: Web框架
- **SQLAlchemy**: 数据库ORM
- **Netmiko**: 网络设备连接
- **APScheduler**: 任务调度
- **Pandas**: 数据处理

### 前端技术
- **Bootstrap 5**: UI框架
- **Font Awesome**: 图标库
- **jQuery**: JavaScript库

### 数据库
- **SQLite**: 默认数据库（开发环境）
- **PostgreSQL/MySQL**: 生产环境推荐

## 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd autonetwork
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 设置安全密钥（生产环境必须）
export SECRET_KEY="your-secret-key-here"
export ENCRYPTION_KEY="your-encryption-key-here"

# 可选配置
export MAX_CONCURRENT_BACKUPS=10
export BACKUP_TIMEOUT=300
export COMPRESS_BACKUPS=true
```

4. **启动系统**
```bash
python run.py
```

5. **访问系统**
- 打开浏览器访问: http://localhost:5000
- 默认账号: admin / admin123

## 使用指南

### 1. 添加设备
1. 进入"设备管理"页面
2. 点击"添加设备"按钮
3. 填写设备信息：
   - 设备别名（可选）
   - 管理IP（必填）
   - 用户名和密码（必填）
   - 端口（默认22）
   - 协议（SSH/Telnet）
   - 设备类型（Cisco IOS/XE/NX-OS）

### 2. 单设备备份
1. 进入"单设备备份"页面
2. 选择要备份的设备
3. 设置备份命令（默认：show running-config）
4. 点击"开始备份"
5. 查看备份进度和结果

### 3. 批量备份
1. 进入"批量备份"页面
2. 下载CSV/Excel模板
3. 填写设备信息并上传文件
4. 选择备份参数
5. 执行批量备份

### 4. 计划任务
1. 进入"系统设置"页面
2. 创建新的计划任务
3. 设置CRON表达式
4. 选择要备份的设备
5. 启用计划任务

## 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask密钥 | dev-secret-key |
| `ENCRYPTION_KEY` | 密码加密密钥 | default-key |
| `DATABASE_URL` | 数据库连接 | sqlite:///backup_system.db |
| `MAX_CONCURRENT_BACKUPS` | 最大并发备份数 | 10 |
| `BACKUP_TIMEOUT` | 备份超时时间（秒） | 300 |
| `COMPRESS_BACKUPS` | 是否压缩备份文件 | false |
| `ENABLE_DIFF` | 是否启用差异比较 | true |

### 文件结构
```
autonetwork/
├── app.py                 # 主应用
├── models.py             # 数据模型
├── device_manager.py     # 设备连接管理
├── backup_service.py     # 备份服务
├── scheduler.py          # 任务调度
├── auth.py               # 用户认证
├── api.py                # API接口
├── import_service.py     # 导入服务
├── config.py             # 配置文件
├── run.py                # 启动脚本
├── requirements.txt       # 依赖包
├── templates/            # 模板文件
│   ├── base.html
│   ├── index.html
│   ├── backup_single.html
│   ├── backup_batch.html
│   ├── devices.html
│   ├── history.html
│   ├── settings.html
│   ├── logs.html
│   └── auth/
│       └── login.html
├── static/               # 静态文件
├── logs/                 # 日志文件
├── backups/              # 备份文件
└── uploads/              # 上传文件
```

## 支持的设备类型

- **Cisco IOS**: 传统IOS设备
- **Cisco IOS-XE**: 新一代IOS-XE设备
- **Cisco NX-OS**: Nexus交换机

## 支持的协议

- **SSH**: 安全连接（推荐）
- **Telnet**: 传统连接

## 常用备份命令

| 命令 | 说明 |
|------|------|
| `show running-config` | 运行配置 |
| `show startup-config` | 启动配置 |
| `show version` | 版本信息 |
| `show inventory` | 硬件清单 |
| `show interfaces` | 接口信息 |
| `show ip route` | 路由表 |

## 故障排除

### 常见问题

1. **连接超时**
   - 检查网络连通性
   - 确认SSH/Telnet服务状态
   - 调整超时时间设置

2. **认证失败**
   - 验证用户名密码
   - 检查设备认证配置
   - 确认enable密码设置

3. **命令执行失败**
   - 检查设备权限
   - 验证命令语法
   - 确认设备类型设置

### 日志查看
- 系统日志: `logs/backup_system.log`
- 任务日志: 通过Web界面查看
- 错误日志: 检查设备连接日志

## 安全建议

1. **生产环境部署**
   - 修改默认密钥
   - 使用HTTPS
   - 配置防火墙
   - 定期备份数据库

2. **密码安全**
   - 使用强密码
   - 定期更换密码
   - 启用密码加密

3. **访问控制**
   - 限制管理员权限
   - 启用审计日志
   - 监控异常访问

## 开发指南

### 添加新功能
1. 在相应模块中添加功能
2. 更新数据模型（如需要）
3. 添加API接口
4. 更新前端界面
5. 编写测试用例

### 自定义设备类型
1. 在`device_manager.py`中添加新设备类型
2. 更新设备类型选项
3. 测试连接和命令执行

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 项目讨论区