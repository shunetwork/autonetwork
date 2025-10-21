# Cisco设备配置备份系统 - 前端

基于Vue 3 + Vite + TypeScript + Element Plus的现代化前端应用。

## 🚀 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **TypeScript** - JavaScript的超集，提供类型安全
- **Element Plus** - Vue 3的UI组件库
- **Vue Router** - Vue.js官方路由管理器
- **Pinia** - Vue的状态管理库
- **Axios** - HTTP客户端

## 📦 安装依赖

### 1. 安装Node.js

请先安装Node.js (推荐版本 18+):

- 访问 [Node.js官网](https://nodejs.org/) 下载并安装
- 或者使用包管理器安装

### 2. 安装项目依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

## 🛠️ 开发

```bash
# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 查看应用

## 📦 构建

```bash
# 构建生产版本
npm run build
```

## 🔧 功能特性

### 配置对比页面
- 🎨 现代化的UI设计
- 📱 响应式布局
- ⚡ 快速加载和渲染
- 🔄 实时数据更新
- 🛡️ TypeScript类型安全
- 📊 直观的差异统计
- 📝 详细的差异显示

### 技术优势
- **类型安全**: TypeScript提供编译时类型检查
- **组件化**: Vue 3 Composition API
- **状态管理**: Pinia提供响应式状态管理
- **路由管理**: Vue Router支持SPA导航
- **UI组件**: Element Plus提供丰富的组件
- **构建优化**: Vite提供快速的开发体验

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/     # 可复用组件
│   ├── views/         # 页面组件
│   ├── stores/        # Pinia状态管理
│   ├── router/        # 路由配置
│   ├── utils/         # 工具函数
│   ├── types/         # TypeScript类型定义
│   └── main.ts        # 应用入口
├── public/            # 静态资源
├── index.html         # HTML模板
├── vite.config.ts     # Vite配置
├── tsconfig.json      # TypeScript配置
└── package.json       # 项目配置
```

## 🎯 主要功能

1. **设备管理** - 添加、编辑、删除网络设备
2. **配置备份** - 单设备和批量备份
3. **配置对比** - 智能对比配置文件差异
4. **备份历史** - 查看备份记录和状态
5. **系统日志** - 查看系统运行日志
6. **系统设置** - 配置系统参数

## 🔗 与后端集成

前端通过代理配置连接到后端API:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true,
    },
  },
}
```

## 📝 开发说明

### 配置对比组件特性

1. **响应式设计**: 适配不同屏幕尺寸
2. **类型安全**: 完整的TypeScript类型定义
3. **状态管理**: 使用Pinia管理应用状态
4. **错误处理**: 完善的错误处理和用户提示
5. **加载状态**: 优雅的加载动画和状态提示
6. **数据格式化**: 智能的时间、文件大小格式化

### 组件结构

- `Compare.vue` - 主配置对比页面
- `stores/compare.ts` - 配置对比状态管理
- 类型定义完整，支持IDE智能提示
- 响应式数据绑定，自动更新UI

## 🚀 部署

1. 构建生产版本: `npm run build`
2. 将 `dist` 目录部署到Web服务器
3. 配置反向代理到后端API

## 📞 支持

如有问题，请查看项目文档或联系开发团队。
