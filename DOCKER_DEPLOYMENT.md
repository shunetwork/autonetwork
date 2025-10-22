# Docker 部署指南

## 概述

本文档介绍如何使用Docker部署Cisco设备备份管理系统。

## 部署方式

### 方式一：使用Docker Compose（推荐）

#### 1. 准备工作

```bash
# 克隆项目
git clone <repository-url>
cd autonetwork

# 创建必要的目录
mkdir -p logs backups data
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要：修改默认密钥）
nano .env
```

**重要配置项：**
- `SECRET_KEY`: 修改为随机字符串
- `ENCRYPTION_KEY`: 修改为随机字符串
- 其他配置根据需要调整

#### 3. 启动服务

```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f autonetwork
```

#### 4. 访问系统

- 访问地址：http://localhost:5000
- 默认账号：admin / admin123

### 方式二：使用Docker命令

#### 1. 构建镜像

```bash
# 构建Docker镜像
docker build -t autonetwork:latest .
```

#### 2. 运行容器

```bash
# 创建数据目录
mkdir -p logs backups data

# 运行容器
docker run -d \
  --name autonetwork \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/backups:/app/backups \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your-secret-key \
  -e ENCRYPTION_KEY=your-encryption-key \
  autonetwork:latest
```

## 生产环境部署

### 使用Nginx反向代理

#### 1. 创建nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream autonetwork {
        server autonetwork:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://autonetwork;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 2. 更新docker-compose.yml

取消注释nginx服务配置，并修改域名。

### 使用外部数据库

#### 1. 修改docker-compose.yml

取消注释postgres服务配置。

#### 2. 更新应用配置

修改应用的环境变量，指向外部数据库。

## 数据持久化

### 重要目录

- `/app/logs`: 系统日志
- `/app/backups`: 备份文件
- `/app/data`: 数据库文件

### 备份数据

```bash
# 备份所有数据
docker-compose exec autonetwork tar -czf /tmp/backup.tar.gz /app/data /app/backups /app/logs

# 复制备份文件
docker cp autonetwork:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

## 监控和维护

### 查看服务状态

```bash
# 查看容器状态
docker-compose ps

# 查看资源使用情况
docker stats

# 查看日志
docker-compose logs -f
```

### 更新服务

```bash
# 停止服务
docker-compose down

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 清理资源

```bash
# 清理未使用的镜像
docker image prune

# 清理未使用的容器
docker container prune

# 清理所有未使用的资源
docker system prune
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :5000
   
   # 修改端口映射
   # 在docker-compose.yml中修改ports配置
   ```

2. **权限问题**
   ```bash
   # 设置目录权限
   chmod 755 logs backups data
   ```

3. **内存不足**
   ```bash
   # 增加Docker内存限制
   # 在docker-compose.yml中添加：
   deploy:
     resources:
       limits:
         memory: 1G
   ```

### 日志查看

```bash
# 查看应用日志
docker-compose logs autonetwork

# 查看系统日志
docker-compose exec autonetwork tail -f /app/logs/backup_system.log
```

## 安全建议

1. **修改默认密钥**
   - 修改SECRET_KEY和ENCRYPTION_KEY
   - 使用强密码

2. **网络安全**
   - 使用HTTPS
   - 配置防火墙
   - 限制访问IP

3. **数据备份**
   - 定期备份数据目录
   - 备份配置文件

## 性能优化

1. **资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '0.5'
   ```

2. **健康检查**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:5000/"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

3. **日志轮转**
   - 配置日志轮转策略
   - 定期清理旧日志

## 联系支持

如有问题，请查看：
- 系统日志：`/app/logs/backup_system.log`
- Docker日志：`docker-compose logs`
- 项目文档：README.md
