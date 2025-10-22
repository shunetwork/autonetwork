# Vue 3前端应用安装指南

## 🚀 安装Node.js

### 方法1: 官网下载
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载LTS版本 (推荐18.x或20.x)
3. 运行安装程序，按默认设置安装
4. 安装完成后重启命令行

### 方法2: 使用包管理器
```bash
# 使用Chocolatey (Windows)
choco install nodejs

# 使用Scoop (Windows)
scoop install nodejs
```

## 📦 验证安装
```bash
node --version
npm --version
```

## 🛠️ 安装前端依赖

### 1. 进入前端目录
```bash
cd frontend
```

### 2. 安装依赖
```bash
npm install
```

### 3. 启动开发服务器
```bash
npm run dev
```

## 🌐 访问应用

- **前端地址**: http://localhost:3000
- **后端地址**: http://127.0.0.1:5000

## 🔧 如果遇到问题

### 问题1: npm命令不存在
**解决方案**: 重新安装Node.js，确保勾选"Add to PATH"选项

### 问题2: 依赖安装失败
**解决方案**: 
```bash
# 清除缓存
npm cache clean --force

# 删除node_modules和package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 问题3: 端口被占用
**解决方案**: 
```bash
# 查看端口占用
netstat -ano | findstr :3000

# 杀死进程
taskkill /PID <进程ID> /F
```

## 📱 功能特性

### 配置对比页面
- 🎨 现代化UI设计
- 📱 响应式布局
- ⚡ 快速加载
- 🔄 实时数据更新
- 📊 智能差异分析

### 技术优势
- 🛡️ TypeScript类型安全
- 🚀 Vite快速构建
- 🎯 Vue 3 Composition API
- 🎨 Element Plus UI组件
- 📦 模块化架构

## 🎉 启动成功后的效果

1. **首页**: 系统功能概览
2. **配置对比**: 美观的对比界面
3. **设备管理**: 完整的设备CRUD
4. **备份管理**: 单设备和批量备份
5. **系统监控**: 日志和统计信息

## 📞 技术支持

如果遇到问题，请检查：
1. Node.js版本 (推荐18+)
2. 网络连接
3. 防火墙设置
4. 端口占用情况

安装完成后，您将拥有一个现代化、美观、稳定的前端应用！
