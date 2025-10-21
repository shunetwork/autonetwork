@echo off
echo ========================================
echo Cisco设备配置备份系统 - 前端安装脚本
echo ========================================
echo.

echo 检查Node.js安装状态...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Node.js
    echo 请先安装Node.js (推荐版本18+)
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js已安装
node --version

echo.
echo 检查npm安装状态...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到npm
    pause
    exit /b 1
)

echo npm已安装
npm --version

echo.
echo 进入前端目录...
cd frontend

echo.
echo 安装项目依赖...
npm install

if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动开发服务器:
echo   cd frontend
echo   npm run dev
echo.
echo 访问地址: http://localhost:3000
echo.
pause
