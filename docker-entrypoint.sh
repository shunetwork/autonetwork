#!/bin/bash

# 等待数据库启动（如果使用外部数据库）
# echo "等待数据库启动..."
# while ! nc -z $DB_HOST $DB_PORT; do
#   sleep 1
# done
# echo "数据库已启动"

# 创建必要的目录
mkdir -p /app/logs
mkdir -p /app/backups
mkdir -p /app/data

# 设置权限
chmod 755 /app/logs
chmod 755 /app/backups
chmod 755 /app/data

# 初始化数据库（如果需要）
# python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 启动应用
echo "启动Cisco设备备份管理系统..."
exec "$@"
