@echo off
REM Cisco设备备份管理系统 - Docker部署脚本 (Windows)

echo ==========================================
echo Cisco设备备份管理系统 - Docker部署
echo ==========================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
echo 创建必要的目录...
if not exist logs mkdir logs
if not exist backups mkdir backups
if not exist data mkdir data

REM 检查环境变量文件
if not exist .env (
    echo 创建环境变量文件...
    (
        echo # 应用配置
        echo FLASK_ENV=production
        echo SECRET_KEY=your-secret-key-here-change-this-in-production
        echo ENCRYPTION_KEY=your-encryption-key-here-change-this-in-production
        echo.
        echo # 日志配置
        echo LOG_LEVEL=INFO
        echo LOG_FILE=/app/logs/backup_system.log
        echo.
        echo # 备份配置
        echo BACKUP_DIR=/app/backups
        echo MAX_BACKUP_FILES=100
        echo.
        echo # 安全配置
        echo SESSION_TIMEOUT=3600
        echo MAX_LOGIN_ATTEMPTS=5
    ) > .env
    echo 已创建 .env 文件，请根据需要修改配置
)

REM 构建镜像
echo 构建Docker镜像...
docker-compose build

REM 启动服务
echo 启动服务...
docker-compose up -d

REM 等待服务启动
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 检查服务状态...
docker-compose ps

echo.
echo ✅ 部署完成！
echo.
echo 访问信息：
echo   地址: http://localhost:5000
echo   默认账号: admin / admin123
echo.
echo 管理命令：
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo   更新服务: docker-compose pull ^&^& docker-compose up -d
echo.
pause
