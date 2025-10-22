#!/bin/bash

# Cisco设备备份管理系统 - Docker部署脚本

set -e

echo "=========================================="
echo "Cisco设备备份管理系统 - Docker部署"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs backups data

# 设置权限
echo "设置目录权限..."
chmod 755 logs backups data

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cat > .env << EOF
# 应用配置
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/backup_system.log

# 备份配置
BACKUP_DIR=/app/backups
MAX_BACKUP_FILES=100

# 安全配置
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
EOF
    echo "已创建 .env 文件，请根据需要修改配置"
fi

# 构建镜像
echo "构建Docker镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "访问信息："
    echo "  地址: http://localhost:5000"
    echo "  默认账号: admin / admin123"
    echo ""
    echo "管理命令："
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo "  更新服务: docker-compose pull && docker-compose up -d"
else
    echo "❌ 服务启动失败，请检查日志："
    docker-compose logs
    exit 1
fi
